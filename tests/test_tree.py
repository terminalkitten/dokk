from pathlib import Path
from typing import Any

from dokk.content import Page
from dokk.routes import assign_routes
from dokk.tree import Node, build_tree, natural_key


def _p(rel: str, title: str = "", **sidebar: Any) -> Page:
    return Page(
        src=Path("/x") / rel,
        rel=Path(rel),
        meta={"sidebar": sidebar} if sidebar else {},
        body="",
        title=title or Path(rel).stem,
    )


def _names(node: Node) -> list[str]:
    return [c.name for c in node.children]


def _tree(*pages: Page) -> Node:
    assign_routes(list(pages), "")
    return build_tree(list(pages))


def test_natural_sort() -> None:
    names = ["step10", "step2", "Step1"]
    assert sorted(names, key=natural_key) == ["Step1", "step2", "step10"]


def test_order_then_name_files_and_folders_interleaved() -> None:
    root = _tree(
        _p("b.md"),
        _p("a.md"),
        _p("z.md", order=1),
        _p("dir/index.md", order=2),
        _p("dir/x.md"),
        _p("item10.md"),
        _p("item9.md"),
    )
    assert _names(root) == ["z", "dir", "a", "b", "item9", "item10"]


def test_hidden_page_and_folder_removed() -> None:
    root = _tree(
        _p("a.md"),
        _p("secret.md", hidden=True),
        _p("private/index.md", hidden=True),
        _p("private/inner.md"),
    )
    assert _names(root) == ["a"]


def test_hidden_home_page_keeps_site() -> None:
    root = _tree(_p("index.md", hidden=True), _p("a.md"))
    assert root.page is None
    assert _names(root) == ["a"]


def test_folder_label_from_index_else_folder_name() -> None:
    root = _tree(
        _p("with-index/index.md", "Indexed Title", label="Short"),
        _p("with-index/a.md"),
        _p("no-index/a.md"),
    )
    labels = {c.name: c.label for c in root.children}
    assert labels == {"with-index": "Indexed Title", "no-index": "No Index"}


def test_page_label_prefers_sidebar_label() -> None:
    root = _tree(_p("a.md", "Title A", label="Label A"), _p("b.md", "Title B"))
    assert [c.label for c in root.children] == ["Label A", "Title B"]


def test_folder_without_index_ordered_last() -> None:
    root = _tree(_p("aaa/x.md"), _p("zzz.md", order=5))
    assert _names(root) == ["zzz", "aaa"]


def test_index_attaches_to_folder() -> None:
    root = _tree(_p("index.md"), _p("g/index.md"), _p("g/h/deep.md"))
    assert root.page and root.page.rel == Path("index.md")
    g = root.children[0]
    assert g.is_dir and g.page and g.page.rel == Path("g/index.md")
    assert g.children[0].is_dir and _names(g.children[0]) == ["deep"]
