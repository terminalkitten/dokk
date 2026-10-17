import shutil
import sys
from pathlib import Path

from jinja2 import Environment

from dokk.assets import ASSETS_DIR, copy_page_assets, copy_public, copy_static
from dokk.config import Config, load_config
from dokk.content import Page, scan
from dokk.markdown import Renderer, pygments_css
from dokk.menu import breadcrumbs, build_menu, ordered_pages, prev_next
from dokk.render import canonical, make_env, render_template
from dokk.routes import assign_routes, output_path
from dokk.tree import Node, build_tree

NOT_FOUND = Path("404.md")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build(root: Path, drafts: bool = False) -> Config:
    cfg = load_config(root)
    pages = scan(cfg.content_dir, drafts)
    not_found = next((p for p in pages if p.rel == NOT_FOUND), None)
    pages = [p for p in pages if p is not not_found]
    assign_routes(pages, cfg.base_path)

    tree = build_tree(pages)
    order = ordered_pages(tree)
    index_pages = {p.rel.parent: p for p in pages if p.rel.stem == "index"}
    env = make_env(cfg)
    page_urls = {p.rel.as_posix(): p.url for p in pages}
    renderer = Renderer(page_urls, cfg.content_dir, cfg.base_path, env)

    out = cfg.out_dir
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
        for href in rendered.broken:
            print(f"warning: {page.rel}: broken link {href!r}", file=sys.stderr)
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
        )
        _write(out / output_path(page.route), html)

    _write(out / "404.html", _render_404(env, tree, not_found, renderer))
    _write(out / ".nojekyll", "")
    return cfg


def _render_404(env: Environment, tree: Node, page: Page | None, renderer: Renderer) -> str:
    body = renderer.render(page.body, page.rel, page.line_offset).html if page else ""
    title = page.title if page else "Page not found"
    return render_template(env, "404.html.jinja", title=title, body=body, menu=build_menu(tree, ""))
