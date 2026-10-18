import re
import unicodedata
from pathlib import Path, PurePosixPath

from dokk import DokkError
from dokk.content import Page


class RouteError(DokkError):
    pass


def slugify(segment: str) -> str:
    # NFC first: macOS file names are NFD, where accents are separate (non-alnum) marks.
    s = unicodedata.normalize("NFC", segment).lower()
    s = re.sub(r"[\s_]+", "-", s)
    s = "".join(c for c in s if c.isalnum() or c == "-")
    return re.sub(r"-{2,}", "-", s).strip("-")


def route_for(rel: Path) -> str:
    parts = list(PurePosixPath(rel.as_posix()).with_suffix("").parts)
    if parts and parts[-1] == "index":
        parts.pop()
    slugs = [slugify(p) for p in parts]
    if any(not s for s in slugs):
        raise RouteError(f"{rel}: cannot build a URL from this path (empty slug)")
    return "/" + "".join(f"{s}/" for s in slugs)


def output_path(route: str) -> Path:
    return Path(route.strip("/")) / "index.html"


def markdown_path(route: str) -> str:
    """Where a page's raw Markdown is published: /guides/intro/ -> guides/intro.md."""
    return (route.strip("/") or "index") + ".md"


def url_for(base_path: str, route: str) -> str:
    return base_path + route


def assign_routes(pages: list[Page], base_path: str) -> None:
    seen: dict[str, Page] = {}
    for page in pages:
        page.route = route_for(page.rel)
        page.url = url_for(base_path, page.route)
        if page.route in seen:
            raise RouteError(
                f"route {page.route} is produced by both {seen[page.route].rel} and {page.rel}"
            )
        seen[page.route] = page
