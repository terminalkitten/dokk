import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from dokk import DokkError

if TYPE_CHECKING:
    from dokk.markdown import TocItem

_FRONT_MATTER = re.compile(r"\A---[ \t]*\r?\n(.*?\r?\n)?---[ \t]*(?:\r?\n|\Z)", re.DOTALL)
_YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)  # C loader is much faster
_LEADING_H1 = re.compile(r"\A\s*#[ \t]+(.+?)[ \t#]*(?:\r?\n|\Z)")


class ContentError(DokkError):
    pass


@dataclass(eq=False)  # pages compare by identity: cheap, and two pages are never "equal"
class Page:
    src: Path  # absolute source path
    rel: Path  # relative to content_dir, e.g. guides/intro.md
    meta: dict[str, Any]  # parsed front matter
    body: str  # Markdown without front matter (and without a title H1)
    title: str = ""  # plain text: sidebar, <title>, breadcrumbs, search
    title_html: str = ""  # the title's inline Markdown rendered, for the page's h1
    title_source: str = ""  # the title as written, for Markdown outputs (page.md, llms)
    description: str = ""
    route: str = ""  # "/guides/intro/" (no base_path)
    url: str = ""  # "/repo/guides/intro/" (with base_path)
    html: str = ""
    toc: list["TocItem"] = field(default_factory=list)  # h2/h3 headings, set by the build
    draft: bool = False
    line_offset: int = 0  # lines before `body` in the source file
    updated: date | None = None  # last modified (git or mtime), set by the build
    has_title: bool = True  # False when the title fell back to the file name

    @property
    def noindex(self) -> bool:
        return self.meta.get("noindex") is True

    @property
    def sidebar(self) -> dict[str, Any]:
        return self.meta.get("sidebar") or {}


def titleize(name: str) -> str:
    words = re.split(r"[-_\s]+", name.strip("-_ "))
    return " ".join(w[:1].upper() + w[1:] for w in words if w)


def split_front_matter(text: str, src: Path) -> tuple[dict[str, Any], str]:
    match = _FRONT_MATTER.match(text)
    if not match:
        return {}, text
    try:
        meta = yaml.load(match.group(1) or "", Loader=_YAML_LOADER) or {}
    except yaml.YAMLError as e:
        raise ContentError(f"{src}: invalid front matter: {e}") from e
    if not isinstance(meta, dict):
        raise ContentError(f"{src}: front matter must be a mapping")
    sidebar = meta.get("sidebar")
    if sidebar is not None and not isinstance(sidebar, dict):
        raise ContentError(f"{src}: 'sidebar' must be a mapping")
    for key in ("title", "description"):
        if meta.get(key) is not None and not isinstance(meta[key], str | int | float):
            raise ContentError(f"{src}: '{key}' must be text")
    order = (sidebar or {}).get("order")
    if order is not None and (isinstance(order, bool) or not isinstance(order, int | float)):
        raise ContentError(f"{src}: 'sidebar.order' must be a number")
    return meta, text[match.end() :]


def load_page(src: Path, content_dir: Path) -> Page:
    rel = src.relative_to(content_dir)
    text = src.read_text(encoding="utf-8")
    meta, body = split_front_matter(text, src)
    title = meta.get("title")
    has_title = True
    if title is None:
        # Title from a leading H1, which is then removed so it is not rendered twice.
        h1 = _LEADING_H1.match(body)
        if h1:
            title, body = h1.group(1), body[h1.end() :]
        else:
            name = src.stem if src.stem != "index" else rel.parent.name
            title = titleize(name) or "Home"
            has_title = False
    return Page(
        src=src,
        rel=rel,
        meta=meta,
        body=body,
        title=str(title),
        description=str(meta.get("description") or ""),
        draft=meta.get("draft") is True,
        has_title=has_title,
        line_offset=text[: len(text) - len(body)].count("\n"),  # body is a suffix of text
    )


def is_hidden(rel: Path) -> bool:
    """Dot files and folders (.git, .obsidian, ...) are never published."""
    return any(part.startswith(".") for part in rel.parts)


def scan(content_dir: Path, drafts: bool = False) -> list[Page]:
    sources = sorted(content_dir.rglob("*.md"))
    pages = [
        load_page(p, content_dir)
        for p in sources
        if p.is_file() and not is_hidden(p.relative_to(content_dir))
    ]
    return [p for p in pages if drafts or not p.draft]
