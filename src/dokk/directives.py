import re
from collections.abc import Callable
from dataclasses import dataclass, field

from markdown_it import MarkdownIt
from markdown_it.rules_block import StateBlock
from markdown_it.rules_inline import StateInline
from markdown_it.token import Token
from markupsafe import Markup
from mdit_py_plugins.container import container_plugin

from dokk import DokkError

CALLOUTS = ("note", "tip", "caution", "danger")
# Parent: its only allowed child. The parent template gets the children as (directive, body).
CHILDREN = {"tabs": "tab", "trace": "step", "models": "model"}
# Children that only exist inside their parent (a ::model also stands on its own).
PARENTS = {"tab": "tabs", "step": "trace"}
# Known directive names
KNOWN = {
    *CALLOUTS,
    *("tabs", "tab", "cards", "card", "steps", "filetree", "linkbutton", "details", "image"),
    *("model", "huggingface", "prompt", "models", "chat", "user", "assistant", "system"),
    *("tool", "trace", "step", "bench", "install", "env"),
}
# Template used by every callout type; not a directive name of its own.
CALLOUT_TEMPLATE = "callout"
BADGE_VARIANTS = {
    "default": "",
    "secondary": "secondary",
    "outline": "outline",
    "danger": "destructive",
}

# Info line
_INFO = re.compile(r"^\s*([A-Za-z][\w-]*)(?:\[(.*?)\])?(?:\{(.*)\})?\s*$")
# Leaf directive
_LEAF = re.compile(r"^::(?!:)(.+)$")  # exactly two colons
# Inline directives
_INLINE = re.compile(r":(badge|kbd|swatch)\[([^\]\n]*)\](?:\{([^}\n]*)\})?")
# CSS color: hex, a name or a function like oklch(0.6 0.2 30)
_COLOR = re.compile(r"[#\w(),.%/\s-]+")
# key="value", or key=value without spaces
_ATTR = re.compile(r'([A-Za-z_][\w-]*)\s*=\s*(?:"([^"]*)"|([^\s"}]+))')
_OPEN, _CLOSE = "container_directive_open", "container_directive_close"


class DirectiveError(DokkError):
    pass


@dataclass
class Directive:
    name: str
    title: str = ""
    attrs: dict[str, str] = field(default_factory=dict)
    line: int = 0  # 1-based line in the Markdown body


def parse_info(info: str) -> Directive | None:
    match = _INFO.match(info)
    if not match:
        return None
    name, title, attrs = match.groups()
    return Directive(name, (title or "").strip(), parse_attrs(attrs or ""))


def parse_attrs(text: str) -> dict[str, str]:
    return {key: quoted or bare for key, quoted, bare in _ATTR.findall(text)}


def _leaf_rule(state: StateBlock, start: int, end: int, silent: bool) -> bool:
    """`::name[label]{attrs}` on its own line: a directive without a body."""
    if state.sCount[start] - state.blkIndent >= 4:  # indented code
        return False
    line = state.src[state.bMarks[start] + state.tShift[start] : state.eMarks[start]]
    match = _LEAF.match(line.rstrip())
    if not match or parse_info(match.group(1)) is None:
        return False
    if silent:
        return True
    for kind, nesting in ((_OPEN, 1), (_CLOSE, -1)):  # an empty container, folded like any other
        token = state.push(kind, "div", nesting)
        token.info, token.markup, token.map = match.group(1), "::", [start, start + 1]
    state.line = start + 1
    return True


def directive_plugin(md: MarkdownIt) -> None:
    container_plugin(
        md,
        "directive",
        validate=lambda params, *args: parse_info(params) is not None,
    )
    alt = ["paragraph", "reference", "blockquote", "list"]
    md.block.ruler.before("fence", "directive_leaf", _leaf_rule, {"alt": alt})
    md.inline.ruler.before("emphasis", "directive_inline", _inline_rule)


def _inline_rule(state: StateInline, silent: bool) -> bool:
    """Text directives: `:badge[Text]{variant="secondary"}`, `:kbd[Ctrl+K]`, `:swatch[#e11d48]`."""
    pos = state.pos
    if state.src[pos] != ":" or (pos and state.src[pos - 1] == ":"):
        return False
    match = _INLINE.match(state.src, pos)
    if not match:
        return False
    name, text, attrs = match.group(1), match.group(2), parse_attrs(match.group(3) or "")
    if name == "badge":
        html = badge(text, attrs.get("variant", "default"))  # validate even when silent
    elif name == "kbd":
        html = Markup('<kbd class="kbd">{}</kbd>').format(text)
    else:
        html = swatch(text)
    if not silent:
        state.push("html_inline", "", 0).content = str(html)
    state.pos = match.end()
    return True


def swatch(color: str) -> Markup:
    """A small color chip; the color is its accessible name."""
    color = color.strip()
    if not _COLOR.fullmatch(color):
        raise DirectiveError(f"swatch {color!r}: not a CSS color")
    return Markup(
        '<span class="dk-swatch" style="--dk-swatch: {0}" role="img" aria-label="{0}" title="{0}">'
        "</span>"
    ).format(color)


def badge(text: str, variant: str) -> Markup:
    """A Basecoat badge; shared by `:badge[...]` and the sidebar's `sidebar.badge`."""
    if variant not in BADGE_VARIANTS:
        allowed = ", ".join(BADGE_VARIANTS)
        raise DirectiveError(f"badge {text!r}: variant must be one of {allowed}")
    data = BADGE_VARIANTS[variant]
    return Markup('<span class="badge"{}>{}</span>').format(
        Markup(' data-variant="{}"').format(data) if data else "", text
    )


# (directive, body_html, child directives with their bodies, raw inner tokens) -> html
RenderDirective = Callable[[Directive, str, list[tuple[Directive, str]], list[Token]], str]


def fold(
    tokens: list[Token],
    render_inner: Callable[[list[Token]], str],
    render_directive: RenderDirective,
    line_offset: int = 0,
    known: set[str] | frozenset[str] = frozenset(KNOWN),
) -> list[Token]:
    """Replace every directive container with one html_block, innermost first.

    `line_offset` is added to token line numbers so errors cite the source file line.
    """
    stack: list[list[Token]] = [[]]
    opens: list[Directive] = []
    for tok in tokens:
        if tok.type == _OPEN:
            directive = parse_info(tok.info)
            assert directive  # validated by the container plugin
            directive.line = (tok.map[0] + 1 + line_offset) if tok.map else 0
            if directive.name not in known:
                raise DirectiveError(
                    f"line {directive.line}: unknown directive ':::{directive.name}'"
                )
            parent = opens[-1].name if opens else None
            if directive.name in PARENTS and parent != PARENTS[directive.name]:
                raise DirectiveError(
                    f"line {directive.line}: ':::{directive.name}' must be inside "
                    f"'::::{PARENTS[directive.name]}'"
                )
            opens.append(directive)
            stack.append([])
        elif tok.type == _CLOSE:
            directive, inner = opens.pop(), stack.pop()
            stack[-1].append(_fold_one(directive, inner, render_inner, render_directive))
        else:
            stack[-1].append(tok)
    return stack[0]


def _fold_one(
    directive: Directive,
    inner: list[Token],
    render_inner: Callable[[list[Token]], str],
    render_directive: RenderDirective,
) -> Token:
    children: list[tuple[Directive, str]] = []
    child_name = CHILDREN.get(directive.name)
    if child_name:
        for tok in inner:
            child = tok.meta.get("directive")
            if not child or child.name != child_name:
                raise DirectiveError(
                    f"line {directive.line}: '::::{directive.name}' may only contain "
                    f"':::{child_name}' blocks (to nest, use more colons on outer fences)"
                )
            children.append((child, tok.meta["body"]))
        body = ""
    else:
        body = render_inner(inner)
    token = Token("html_block", "", 0)
    token.meta = {"directive": directive, "body": body}
    if directive.name in PARENTS:
        token.content = ""
    else:
        token.content = render_directive(directive, body, children, inner)
    return token
