import re
import tempfile
from dataclasses import dataclass
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlsplit

from dokk import DokkError
from dokk.build import build
from dokk.routes import output_path

_URL = re.compile(r'(?:href|src)="([^"]*)"')
_ID = re.compile(r'\sid="([^"]+)"')
_HEADING = re.compile(r"<h([1-6])[\s>]")
_ARTICLE = re.compile(r'<article class="dk-prose">(.*?)</article>', re.DOTALL)


@dataclass(frozen=True)
class Issue:
    level: str  # "error" or "warning"
    source: str  # page source path, relative to content_dir
    message: str

    def __str__(self) -> str:
        return (
            f"{self.level}: {self.source}: {self.message}"
            if self.source
            else f"{self.level}: {self.message}"
        )


def check(root: Path) -> list[Issue]:
    """Production build into a temp dir, then crawl it for broken links, anchors and assets."""
    with tempfile.TemporaryDirectory() as tmp:
        try:
            result = build(root, out_dir=Path(tmp) / "site", search=False, parallel=True)
        except DokkError as e:  # duplicate routes, bad front matter, unknown directives...
            return [Issue("error", "", str(e))]

        issues: list[Issue] = []
        prefix = result.cfg.base_path + "/"
        ids: dict[Path, set[str]] = {}

        def ids_of(file: Path) -> set[str]:
            if file not in ids:
                ids[file] = set(_ID.findall(file.read_text(encoding="utf-8")))
            return ids[file]

        for page in result.pages:
            source = page.rel.as_posix()
            if not page.has_title:
                issues.append(Issue("warning", source, f"no title, using {page.title!r}"))
            for href in result.broken.get(page.rel, []):
                issues.append(Issue("error", source, f"broken link {href!r}"))

            file = result.out_dir / output_path(page.route)
            html = file.read_text(encoding="utf-8")
            issues += heading_issues(source, html)
            seen = set()
            for url in map(unescape, _URL.findall(html)):
                if url in seen or urlsplit(url).scheme or url.startswith("//"):
                    continue
                seen.add(url)
                path, _, fragment = url.partition("#")
                if not path:
                    target = file
                elif path.startswith(prefix):
                    target = result.out_dir / unquote(path[len(prefix) :])
                    if target.is_dir():
                        target = target / "index.html"
                    if not target.is_file():
                        issues.append(Issue("error", source, f"link target not found: {url}"))
                        continue
                else:
                    continue  # unresolved relative links are already reported as broken
                if (
                    fragment
                    and target.suffix == ".html"
                    and unquote(fragment) not in ids_of(target)
                ):
                    issues.append(Issue("error", source, f"missing anchor: {url}"))
        if result.cfg.sidebar:  # the automatic menu always lists every non-hidden page
            in_menu = set(result.menu_pages)
            for page in result.pages:
                if page not in in_menu and not page.sidebar.get("hidden"):
                    msg = "not in the sidebar (add it, or set sidebar.hidden: true)"
                    issues.append(Issue("warning", page.rel.as_posix(), msg))
        return issues


def heading_issues(source: str, html: str) -> list[Issue]:
    """Exactly one h1 per page and no skipped heading levels, inside the article."""
    article = _ARTICLE.search(html)
    levels = [int(n) for n in _HEADING.findall(article.group(1))] if article else []
    issues = []
    if levels.count(1) != 1:
        issues.append(Issue("warning", source, f"expected one <h1>, found {levels.count(1)}"))
    for prev, cur in zip(levels, levels[1:], strict=False):
        if cur > prev + 1:
            issues.append(Issue("warning", source, f"heading level skipped: h{prev} to h{cur}"))
    return issues
