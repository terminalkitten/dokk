"""Directives compiled to static HTML: `:::name[Title]{key="value"}` containers and
`::name[Title]{key="value"}` one-line (leaf) directives, from the generic directives syntax.

All directives are parsed as one container type; `fold` then replaces each
container (innermost first) with a single html_block holding the rendered component.
"""

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
CHILDREN = {"tabs": "tab"}  # parent: only allowed child
PARENTS = {child: parent for parent, child in CHILDREN.items()}
KNOWN = {*CALLOUTS, "tabs", "tab", "cards", "card", "steps", "filetree", "linkbutton", "details"}
BADGE_VARIANTS = {
    "default": "",
    "secondary": "secondary",
    "outline": "outline",
    "danger": "destructive",
}

_INFO = re.compile(r"^\s*([A-Za-z][\w-]*)(?:\[(.*?)\])?(?:\{(.*)\})?\s*$")
_LEAF = re.compile(r"^::(?!:)(.+)$")  # exactly two colons
_INLINE = re.compile(r":(badge|kbd|swatch)\[([^\]\n]*)\](?:\{([^}\n]*)\})?")
# A CSS color: hex, a name or a function like oklch(0.6 0.2 30); nothing that ends the property.
_COLOR = re.compile(r"[#\w(),.%/\s-]+")
_ATTR = re.compile(r'([A-Za-z_][\w-]*)\s*=\s*"([^"]*)"')
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
    return Directive(name, (title or "").strip(), dict(_ATTR.findall(attrs or "")))


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
    name, text, attrs = match.group(1), match.group(2), dict(_ATTR.findall(match.group(3) or ""))
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
            if directive.name not in KNOWN:
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
