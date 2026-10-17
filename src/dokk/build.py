import shutil
from pathlib import Path

from jinja2 import Environment
from markdown_it import MarkdownIt

from dokk.config import Config, load_config
from dokk.content import Page, scan
from dokk.markdown import make_md, render_markdown
from dokk.menu import breadcrumbs, build_menu, ordered_pages, prev_next
from dokk.render import canonical, make_env, render_template
from dokk.routes import assign_routes, output_path
from dokk.tree import Node, build_tree

STATIC = Path(__file__).parent / "static"
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
    md = make_md()

    out = cfg.out_dir
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(STATIC, out / "_dokk")
    public = cfg.root / "public"
    if public.is_dir():
        shutil.copytree(public, out, dirs_exist_ok=True)

    for page in pages:
        page.html = render_markdown(md, page.body)
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

    _write(out / "404.html", _render_404(env, tree, not_found, md))
    _write(out / ".nojekyll", "")
    return cfg


def _render_404(env: Environment, tree: Node, page: Page | None, md: MarkdownIt) -> str:
    body = render_markdown(md, page.body) if page else ""
    title = page.title if page else "Page not found"
    return render_template(env, "404.html.jinja", title=title, body=body, menu=build_menu(tree, ""))
