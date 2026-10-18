import shutil
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

from jinja2 import Environment

from dokk.assets import ASSETS_DIR, copy_page_assets, copy_public, copy_static
from dokk.config import Config, load_config
from dokk.content import Page, scan
from dokk.markdown import Renderer, pygments_css
from dokk.menu import breadcrumbs, build_menu, ordered_pages, prev_next
from dokk.render import canonical, make_env, render_template
from dokk.routes import assign_routes, output_path
from dokk.search import build_index, search_available
from dokk.seo import last_modified, robots, sitemap
from dokk.tree import Node, build_tree

NOT_FOUND = Path("404.md")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@dataclass
class BuildResult:
    cfg: Config
    out_dir: Path
    pages: list[Page]
    menu_pages: list[Page]  # pages reachable from the menu, in menu order
    broken: dict[Path, list[str]] = field(default_factory=dict)  # source rel -> hrefs
    search: bool = False  # a Pagefind index was built
    search_missing: bool = False  # search is enabled but pagefind is not installed


def build(
    root: Path,
    drafts: bool = False,
    dev: bool = False,
    out_dir: Path | None = None,
    search: bool | None = None,
) -> BuildResult:
    """Build the site.

    `dev` drops base_path and injects the reload script. `search` overrides
    `search.enabled` from dokk.toml (default on when pagefind is installed).
    """
    cfg = load_config(root, dev=dev)
    want_search = bool(cfg.search.get("enabled", True)) if search is None else search
    with_search = want_search and search_available()
    pages = scan(cfg.content_dir, drafts)
    not_found = next((p for p in pages if p.rel == NOT_FOUND), None)
    pages = [p for p in pages if p is not not_found]
    assign_routes(pages, cfg.base_path)

    tree = build_tree(pages)
    order = ordered_pages(tree)
    index_pages = {p.rel.parent: p for p in pages if p.rel.stem == "index"}
    env = make_env(cfg, dev=dev, search=with_search)
    page_urls = {p.rel.as_posix(): p.url for p in pages}
    renderer = Renderer(page_urls, cfg.content_dir, cfg.base_path, env)

    out = out_dir or cfg.out_dir
    result = BuildResult(
        cfg, out, pages, order, search=with_search, search_missing=want_search and not with_search
    )
    updated = last_modified(cfg.content_dir, pages)
    if out.exists():
        shutil.rmtree(out)
    copy_static(out)
    copy_page_assets(cfg.content_dir, out)
    copy_public(cfg.root, out)
    _write(
        out / ASSETS_DIR / "pygments.css",
        pygments_css(cfg.theme["code_light"], cfg.theme["code_dark"]),
    )

    for page in pages:
        rendered = renderer.render(page.body, page.rel, page.line_offset)
        page.html, page.toc = rendered.html, rendered.toc
        page.description = page.description or rendered.description
        page.updated = updated[page.rel]
        if rendered.broken:
            result.broken[page.rel] = rendered.broken
        prev, next_ = prev_next(order, page)
        html = render_template(
            env,
            "page.html.jinja",
            page=page,
            menu=build_menu(tree, page.route),
            crumbs=breadcrumbs(page, index_pages),
            prev=prev,
            next=next_,
            canonical=canonical(cfg, page.route),
            edit_url=_edit_url(cfg, page),
        )
        _write(out / output_path(page.route), html)

    _write(out / "404.html", _render_404(env, tree, not_found, renderer))
    _write(out / ".nojekyll", "")
    if cfg.site_url:
        indexed = [(canonical(cfg, p.route), p.updated) for p in pages if not p.noindex]
        _write(out / "sitemap.xml", sitemap(sorted(indexed, key=lambda e: e[0])))
    if not (out / "robots.txt").exists():  # a robots.txt in public/ wins
        _write(out / "robots.txt", robots(canonical(cfg, "/sitemap.xml")))
    if with_search:
        build_index(out)
    return result


def _edit_url(cfg: Config, page: Page) -> str:
    template = str(cfg.links.get("edit_url", ""))
    return template.replace("{path}", quote(page.rel.as_posix())) if template else ""


def _render_404(env: Environment, tree: Node, page: Page | None, renderer: Renderer) -> str:
    body = renderer.render(page.body, page.rel, page.line_offset).html if page else ""
    title = page.title if page else "Page not found"
    return render_template(env, "404.html.jinja", title=title, body=body, menu=build_menu(tree, ""))
