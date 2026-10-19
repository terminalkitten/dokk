import itertools
import posixpath
import re
import textwrap
from collections import defaultdict
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, cast
from urllib.parse import quote, unquote, urlsplit

from jinja2 import Environment
from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML
from markdown_it.token import Token
from markupsafe import Markup
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.attrs import attrs_plugin
from mdit_py_plugins.deflist import deflist_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.lexers.special import TextLexer
from pygments.util import ClassNotFound

from dokk import DokkError
from dokk.directives import (
    CALLOUT_TEMPLATE,
    CALLOUTS,
    KNOWN,
    Directive,
    DirectiveError,
    directive_plugin,
    fold,
)
from dokk.filetree import file_tree
from dokk.headings import heading_attrs_plugin, strip_attrs

DESCRIPTION_LENGTH = 160
LINKBUTTON_VARIANTS = ("primary", "secondary", "minimal")
HUGGINGFACE_TYPES = ("model", "dataset", "space")


@dataclass(frozen=True)
class TocItem:
    level: int
    id: str
    text: str


@dataclass
class Rendered:
    html: str
    toc: list[TocItem] = field(default_factory=list)
    description: str = ""  # plain text of the first paragraph, truncated
    broken: list[str] = field(default_factory=list)  # unresolved links and assets


_TITLE = re.compile(r'title="([^"]*)"')
_LINES = re.compile(r"\{([\d,\s-]+)\}")


def _line_numbers(spec: str) -> list[int]:
    """ "2,4-6" -> [2, 4, 5, 6]"""
    lines: list[int] = []
    for part in filter(None, (p.strip() for p in spec.split(","))):
        start, _, end = part.partition("-")
        lines += range(int(start), int(end or start) + 1)
    return lines


def highlight_code(code: str, lang: str, attrs: str) -> str:
    """A code block, highlighted at build time. `attrs` is the rest of the fence's info
    string: title="file.py" adds a caption, {2,4-6} highlights lines."""
    try:
        lexer = get_lexer_by_name(lang) if lang else TextLexer()
    except ClassNotFound:
        lexer = TextLexer()
    lines = _LINES.search(attrs)
    formatter = HtmlFormatter(nowrap=True, hl_lines=_line_numbers(lines.group(1)) if lines else [])
    code_html = Markup(highlight(code, lexer, formatter))  # Pygments escapes the code
    html = Markup('<pre class="code hl"><code class="language-{}">{}</code></pre>').format(
        lang or "text", code_html
    )
    title = _TITLE.search(attrs)
    if title:
        html = Markup('<figure class="dk-codeblock"><figcaption>{}</figcaption>{}</figure>').format(
            title.group(1), html
        )
    return str(html)  # plain str: markdown-it concatenates, and str + Markup escapes the str


def _fence(self: Any, tokens: Sequence[Token], idx: int, options: Any, env: Any) -> str:
    info = tokens[idx].info.strip()
    lang, _, attrs = info.partition(" ")
    return highlight_code(tokens[idx].content, lang, attrs) + "\n"


def _table_open(self: Any, tokens: Sequence[Token], idx: int, options: Any, env: Any) -> str:
    tokens[idx].attrSet("class", "table")
    return '<div class="table-container">' + self.renderToken(tokens, idx, options, env)


def _table_close(self: Any, tokens: Sequence[Token], idx: int, options: Any, env: Any) -> str:
    return self.renderToken(tokens, idx, options, env) + "</div>"


def make_md() -> MarkdownIt:
    md = (
        MarkdownIt("commonmark", {"html": True, "typographer": True})
        .enable(["table", "strikethrough", "replacements", "smartquotes"])
        .use(anchors_plugin, min_level=2, max_level=3, permalink=True, permalinkSymbol="#")
        .use(footnote_plugin)
        .use(tasklists_plugin, label=True)  # label: checkboxes need an accessible name
        .use(deflist_plugin)
        .use(attrs_plugin)
        .use(directive_plugin)
        .use(heading_attrs_plugin)
    )
    md.add_render_rule("fence", _fence)
    md.add_render_rule("table_open", _table_open)
    md.add_render_rule("table_close", _table_close)
    return md


def _plain_text(inline: Token) -> str:
    """Text of an inline token, without markup and without the heading permalink."""
    parts = []
    for child in inline.children or []:
        if child.type == "link_open" and child.attrGet("class") == "header-anchor":
            break
        if child.type in ("text", "code_inline"):
            parts.append(child.content)
        elif child.type in ("softbreak", "hardbreak"):
            parts.append(" ")
    return "".join(parts).strip()


_TITLE_MD = MarkdownIt("commonmark", {"html": False})  # titles: inline Markdown, HTML escaped


def render_title(source: str) -> tuple[Markup, str]:
    """A title in Markdown: (HTML for the h1, plain text for everything else)."""
    inline = _TITLE_MD.parseInline(strip_attrs(source))[0]
    html = _TITLE_MD.renderer.render(inline.children or [], _TITLE_MD.options, {})
    return Markup(html.strip()), _plain_text(inline)


def _truncate(text: str, limit: int = DESCRIPTION_LENGTH) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",.;:") + "…"


def _is_external(href: str) -> bool:
    parts = urlsplit(href)
    return bool(parts.scheme or parts.netloc)


class Renderer:
    """Renders page bodies; rewrites relative links and assets to root-absolute URLs.

    `page_urls` maps a source path (relative to content_dir, POSIX) to its page URL.
    `content_dir` is used to check that linked assets exist.
    `env` renders directive components from `components/<name>.html.jinja`.
    """

    def __init__(
        self,
        page_urls: dict[str, str],
        content_dir: Path,
        base_path: str,
        env: Environment,
    ) -> None:
        self.md = make_md()
        self.page_urls = page_urls
        self.content_dir = content_dir
        self.base_path = base_path
        self.env = env
        self.known = KNOWN | component_names(env)

    def render(self, body: str, rel: Path, line_offset: int = 0) -> Rendered:
        env: dict[str, Any] = {}
        try:
            tokens = self.md.parse(body, env)
        except DirectiveError as e:  # raised by inline directives such as :badge
            raise DirectiveError(f"{rel}: {e}") from None
        result = Rendered(html="")
        source_dir = PurePosixPath(rel.as_posix()).parent
        for i, tok in enumerate(tokens):
            if tok.type == "heading_open" and tok.tag in ("h2", "h3") and tok.attrGet("id"):
                text = _plain_text(tokens[i + 1])
                result.toc.append(TocItem(int(tok.tag[1]), str(tok.attrGet("id")), text))
            elif tok.type == "paragraph_open" and not result.description:
                result.description = _truncate(_plain_text(tokens[i + 1]))
            if tok.type == "inline":
                self._rewrite(tok.children or [], source_dir, result.broken)
        # Explicit per-page ids (dk-tabs-1, dk-image-2, ...) keep builds deterministic.
        counters: dict[str, Iterator[int]] = defaultdict(lambda: itertools.count(1))

        renderer = cast(RendererHTML, self.md.renderer)  # MarkdownIt's default renderer
        lines = body.splitlines()

        def render_inner(inner: list[Token]) -> str:
            return renderer.render(inner, self.md.options, env)

        def render_inline(inline: list[Token]) -> str:
            return renderer.renderInline(inline, self.md.options, env)

        def render_directive(
            d: Directive, body: str, children: list[tuple[Directive, str]], inner: list[Token]
        ) -> str:
            extra: dict[str, Any] = {}
            if d.name == "filetree":
                try:
                    extra["entries"] = file_tree(inner, render_inline)
                except DokkError as e:
                    raise DirectiveError(f"line {d.line}: {e}") from None
            if d.name == "image" and (not d.title or not d.attrs.get("src")):
                raise DirectiveError(f'line {d.line}: use ::image[Alt text]{{src="..."}}')
            if d.name in ("model", "huggingface") and not d.title:
                raise DirectiveError(f"line {d.line}: use ::{d.name}[Name]")
            if d.name == "huggingface" and d.attrs.get("type", "model") not in HUGGINGFACE_TYPES:
                types = ", ".join(HUGGINGFACE_TYPES)
                raise DirectiveError(f"line {d.line}: huggingface type must be one of {types}")
            if d.name == "prompt":  # copied as written, Markdown and all
                extra["source"] = _source(lines, inner)
            if d.name == "linkbutton":
                if not d.title or not d.attrs.get("href"):
                    raise DirectiveError(f'line {d.line}: use ::linkbutton[Text]{{href="..."}}')
                if d.attrs.get("variant", "primary") not in LINKBUTTON_VARIANTS:
                    variants = ", ".join(LINKBUTTON_VARIANTS)
                    raise DirectiveError(
                        f"line {d.line}: linkbutton variant must be one of {variants}"
                    )
                extra["external"] = _is_external(d.attrs["href"])
            for attr in ("href", "src"):  # relative links and files, as in Markdown
                value = d.attrs.get(attr)
                if value:
                    resolved = self._resolve(value, source_dir, is_link=attr == "href")
                    if resolved is None:
                        result.broken.append(value)
                    d.attrs[attr] = resolved or value
            name = CALLOUT_TEMPLATE if d.name in CALLOUTS else d.name
            return self.env.get_template(f"components/{name}.html.jinja").render(
                directive=d,
                body=Markup(body),
                children=[(c, Markup(b)) for c, b in children],
                id=f"dk-{d.name}-{next(counters[d.name])}",
                **extra,
            )

        try:
            tokens = fold(tokens, render_inner, render_directive, line_offset, self.known)
        except DirectiveError as e:
            raise DirectiveError(f"{rel}: {e}") from None
        result.html = render_inner(tokens)
        return result

    def _rewrite(self, children: list[Token], source_dir: PurePosixPath, broken: list[str]) -> None:
        for child in children:
            if child.type == "link_open":
                attr = "href"
            elif child.type == "image":
                attr = "src"
            else:
                continue
            value = str(child.attrGet(attr) or "")
            new = self._resolve(value, source_dir, is_link=attr == "href")
            if new is None:
                broken.append(value)
            else:
                child.attrSet(attr, new)
            # Images load as they scroll into view; {loading=eager} on an image opts out.
            if child.type == "image":
                for key, value in (("loading", "lazy"), ("decoding", "async")):
                    if child.attrGet(key) is None:
                        child.attrSet(key, value)

    def _resolve(self, href: str, source_dir: PurePosixPath, is_link: bool) -> str | None:
        """New URL for `href`, or None if it points to a missing page or file."""
        if not href or href.startswith("#") or _is_external(href):
            return href
        path, _, fragment = href.partition("#")
        fragment = f"#{fragment}" if fragment else ""
        if path.startswith("/"):
            base = self.base_path
            if base and (path == base or path.startswith(base + "/")):
                return href
            return base + href
        target = posixpath.normpath(str(source_dir / unquote(path)))
        if target == ".." or target.startswith("../"):
            return None  # outside content_dir
        if is_link and target.endswith(".md"):
            url = self.page_urls.get(target)
            return url + fragment if url else None
        if not (self.content_dir / target).is_file():
            return None
        return f"{self.base_path}/{quote(target)}{fragment}"


def _source(lines: list[str], inner: list[Token]) -> str:
    """The Markdown inside a directive, as written."""
    maps = [t.map for t in inner if t.map]
    if not maps:
        return ""
    start, end = min(m[0] for m in maps), max(m[1] for m in maps)
    return textwrap.dedent("\n".join(lines[start:end])).strip()


def component_names(env: Environment) -> set[str]:
    """Directive names from `components/<name>.html.jinja`, built in or in the site's
    templates/: adding a template there registers a component."""
    names = {
        t.removeprefix("components/").removesuffix(".html.jinja")
        for t in env.list_templates()
        if t.startswith("components/") and t.endswith(".html.jinja") and t.count("/") == 1
    }
    return names - {CALLOUT_TEMPLATE}


def pygments_css(light: str, dark: str) -> str:
    """Token CSS for both themes, scoped so neither leaks into the other."""
    css = []
    for style, scope in (
        (light, "html:not(.dark) .dk-prose .hl"),
        (dark, "html.dark .dk-prose .hl"),
    ):
        defs = HtmlFormatter(style=style).get_style_defs(scope)
        # .hll (highlighted lines) is styled in dokk.css so it works with every style.
        css += [
            line for line in defs.splitlines() if line.startswith(scope) and " .hll " not in line
        ]
    # Drop Pygments' per-rule "/* Token */" comments: about 40% of the file.
    return "\n".join(re.sub(r"\s*/\*.*?\*/", "", line) for line in css) + "\n"
