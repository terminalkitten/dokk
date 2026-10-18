import os
import re
import shutil
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

from jinja2 import Environment
from markupsafe import Markup

from dokk.assets import ASSETS_DIR, copy_page_assets, copy_public, copy_static
from dokk.config import Config, load_config
from dokk.content import Page, scan
from dokk.llms import llms_sections
from dokk.markdown import Rendered, Renderer, pygments_css
from dokk.menu import (
    Nav,
    Pager,
    auto_nav,
    breadcrumbs,
    build_menu,
    config_nav,
    mark_current,
    ordered_pages,
    submenu_keys,
)
from dokk.render import canonical, make_env, render_template
from dokk.routes import assign_routes, markdown_path, output_path, url_for
from dokk.search import build_index, search_available
from dokk.seo import last_modified
from dokk.themes import theme_vars
from dokk.tree import build_tree
from dokk.writer import SiteWriter

NOT_FOUND = Path("404.md")
# ponytail: below this, starting worker processes costs more than it saves.
PARALLEL_MIN_PAGES = 200


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
    parallel: bool = False,
) -> BuildResult:
    """Build the site.

    `dev` drops base_path and injects the reload script. `search` overrides
    `search.enabled` from dokk.toml (default on when pagefind is installed).
    `parallel` renders Markdown in worker processes on big sites; the caller's main
    module must be import-safe (an `if __name__ == "__main__"` guard), as the CLI is.
    """
    cfg = load_config(root, dev=dev)
    want_search = bool(cfg.search.get("enabled", True)) if search is None else search
    with_search = want_search and search_available()
    pages = scan(cfg.content_dir, drafts)
    not_found = next((p for p in pages if p.rel == NOT_FOUND), None)
    pages = [p for p in pages if p is not not_found]
    assign_routes(pages, cfg.base_path)

    nav = _nav(cfg, pages)
    order = ordered_pages(nav)
    pager = Pager(order)
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
    copy_static(out, cfg.theme["style"])
    copy_page_assets(cfg.content_dir, out)
    copy_public(cfg.root, out)
    writer = SiteWriter(env, out)
    _write_theme(writer, cfg)

    sidebar = Sidebar(env, nav)
    all_rendered = _render_markdown(cfg, page_urls, pages, renderer, parallel, dev, with_search)
    for page, rendered in zip(pages, all_rendered, strict=True):
        page.html, page.toc = rendered.html, rendered.toc
        page.description = page.description or rendered.description
        page.updated = updated[page.rel]
        if rendered.broken:
            result.broken[page.rel] = rendered.broken
        prev, next_ = pager(page)
        writer.render(
            output_path(page.route),
            "page.html.jinja",
            page=page,
            sidebar_html=sidebar.for_page(page),
            crumbs=breadcrumbs(page, index_pages),
            prev=prev,
            next=next_,
            canonical=canonical(cfg, page.route),
            edit_url=_edit_url(cfg, page),
            md_url=url_for(cfg.base_path, "/" + markdown_path(page.route)),
            ask_url=_ask_url(cfg, page),
        )
        writer.render(markdown_path(page.route), "files/page.md.jinja", page=page)

    writer.render(
        "404.html",
        "404.html.jinja",
        title=not_found.title if not_found else "Page not found",
        body=renderer.render(not_found.body, not_found.rel, not_found.line_offset).html
        if not_found
        else "",
        sidebar_html=sidebar.for_page(None),
    )
    _write_site_files(writer, cfg, pages, nav, order)
    if with_search:
        build_index(out)
    return result


def _nav(cfg: Config, pages: list[Page]) -> list[Nav]:
    """The sidebar: from [[sidebar]] in dokk.toml, else generated from the folders."""
    tree = build_tree(pages)
    if not cfg.sidebar:
        return auto_nav(tree)
    by_rel = {p.rel.as_posix(): p for p in pages}
    return config_nav(cfg.sidebar, tree, by_rel, cfg.content_dir, cfg.base_path)


def _write_theme(writer: SiteWriter, cfg: Config) -> None:
    """Code highlighting and color tokens; the style pack itself is a static file."""
    theme = cfg.theme
    writer.text(f"{ASSETS_DIR}/pygments.css", pygments_css(theme["code_light"], theme["code_dark"]))
    base, color = theme["base"], theme["color"]
    writer.render(
        f"{ASSETS_DIR}/theme.css",
        "files/theme.css.jinja",
        base=base,
        color=color,
        vars=theme_vars(base, color),
    )


def _write_site_files(
    writer: SiteWriter, cfg: Config, pages: list[Page], nav: list[Nav], order: list[Page]
) -> None:
    """Files for hosts, crawlers and AI tools: .nojekyll, sitemap, robots, llms."""
    writer.text(".nojekyll", "")
    if cfg.site_url:
        indexed = sorted((canonical(cfg, p.route), p.updated) for p in pages if not p.noindex)
        writer.render("sitemap.xml", "files/sitemap.xml.jinja", entries=indexed)
    if not (writer.root / "robots.txt").exists():  # a robots.txt in public/ wins
        writer.render(
            "robots.txt", "files/robots.txt.jinja", sitemap_url=canonical(cfg, "/sitemap.xml")
        )
    if cfg.llms.get("enabled"):

        def absolute(p: Page) -> str:
            return canonical(cfg, p.route) or p.url

        writer.render(
            "llms.txt", "files/llms.txt.jinja", sections=llms_sections(nav), absolute=absolute
        )
        in_menu = set(order)
        full = [p for p in order + [p for p in pages if p not in in_menu] if not p.noindex]
        writer.render("llms-full.txt", "files/llms-full.txt.jinja", pages=full, absolute=absolute)


def _ask_url(cfg: Config, page: Page) -> str:
    """URL-encoded prompt for "Open in ChatGPT/Claude"; needs a public site_url."""
    url = canonical(cfg, page.route)
    return quote(f"Read from {url} so I can ask questions about it.") if url else ""


def _edit_url(cfg: Config, page: Page) -> str:
    template = str(cfg.links.get("edit_url", ""))
    return template.replace("{path}", quote(page.rel.as_posix())) if template else ""


_worker_renderer: Renderer | None = None


def _init_worker(cfg: Config, page_urls: dict[str, str], dev: bool, search: bool) -> None:
    global _worker_renderer
    env = make_env(cfg, dev=dev, search=search)  # same globals as the main process
    _worker_renderer = Renderer(page_urls, cfg.content_dir, cfg.base_path, env)


def _render_in_worker(job: tuple[str, Path, int]) -> Rendered:
    assert _worker_renderer
    return _worker_renderer.render(*job)


def _render_markdown(
    cfg: Config,
    page_urls: dict[str, str],
    pages: list[Page],
    renderer: Renderer,
    parallel: bool,
    dev: bool,
    search: bool,
) -> list[Rendered]:
    """Markdown is the slowest step and pages are independent: use all cores on big sites."""
    jobs = [(p.body, p.rel, p.line_offset) for p in pages]
    workers = os.cpu_count() or 1
    if parallel and len(pages) >= PARALLEL_MIN_PAGES and workers > 1:
        initargs = (cfg, page_urls, dev, search)
        chunk = max(1, len(jobs) // (workers * 4))
        try:
            with ProcessPoolExecutor(workers, initializer=_init_worker, initargs=initargs) as pool:
                return list(pool.map(_render_in_worker, jobs, chunksize=chunk))
        except BrokenProcessPool:
            pass  # e.g. an unguarded __main__; fall back to one process
    return [renderer.render(*job) for job in jobs]


class Sidebar:
    """Renders the sidebar once; each page then gets its current link and open submenus.

    Re-rendering ~1000 menu items for each of ~1000 pages was most of the build time.
    """

    def __init__(self, env: Environment, nav: list[Nav]) -> None:
        keys, self.around = submenu_keys(nav)
        html = render_template(env, "partials/sidebar.html.jinja", menu=build_menu(nav, keys))
        # The macro's indentation is about half the bytes, and it is repeated on every page.
        self.html = re.sub(r"\s+", " ", html)  # safe: the sidebar has no <pre>

    def for_page(self, page: Page | None) -> Markup:
        around = self.around.get(page) if page else None
        if page is None or around is None:  # not in the menu
            return Markup(self.html)
        return Markup(mark_current(self.html, page.url, around))
