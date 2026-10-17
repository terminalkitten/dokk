import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from dokk import DokkError

_FRONT_MATTER = re.compile(r"\A---[ \t]*\r?\n(.*?\r?\n)?---[ \t]*(?:\r?\n|\Z)", re.DOTALL)
_LEADING_H1 = re.compile(r"\A\s*#[ \t]+(.+?)[ \t#]*(?:\r?\n|\Z)")


class ContentError(DokkError):
    pass


@dataclass
class Page:
    src: Path  # absolute source path
    rel: Path  # relative to content_dir, e.g. guides/intro.md
    meta: dict[str, Any]  # parsed front matter
    body: str  # Markdown without front matter (and without a title H1)
    title: str = ""
    description: str = ""
    route: str = ""  # "/guides/intro/" (no base_path)
    url: str = ""  # "/repo/guides/intro/" (with base_path)
    html: str = ""
    toc: list[Any] = field(default_factory=list)  # filled in Phase 2
    draft: bool = False
    line_offset: int = 0  # lines before `body` in the source file
    has_title: bool = True  # False when the title fell back to the file name

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
        meta = yaml.safe_load(match.group(1) or "") or {}
    except yaml.YAMLError as e:
        raise ContentError(f"{src}: invalid front matter: {e}") from e
    if not isinstance(meta, dict):
        raise ContentError(f"{src}: front matter must be a mapping")
    sidebar = meta.get("sidebar")
    if sidebar is not None and not isinstance(sidebar, dict):
        raise ContentError(f"{src}: 'sidebar' must be a mapping")
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
        description=str(meta.get("description", "")),
        draft=meta.get("draft") is True,
        has_title=has_title,
        line_offset=text[: len(text) - len(body)].count("\n"),  # body is a suffix of text
    )


def scan(content_dir: Path, drafts: bool = False) -> list[Page]:
    pages = [load_page(p, content_dir) for p in sorted(content_dir.rglob("*.md")) if p.is_file()]
    return [p for p in pages if drafts or not p.draft]
