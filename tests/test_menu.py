from pathlib import Path
from typing import Any

from dokk.content import Page
from dokk.menu import breadcrumbs, build_menu, ordered_pages, prev_next
from dokk.routes import assign_routes
from dokk.tree import build_tree


def _p(rel: str, title: str = "", **sidebar: Any) -> Page:
    return Page(
        src=Path("/x") / rel,
        rel=Path(rel),
        meta={"sidebar": sidebar} if sidebar else {},
        body="",
        title=title or Path(rel).stem,
    )


PAGES = [
    _p("index.md", "Home"),
    _p("about.md", "About"),
    _p("guides/index.md", "Guides", label="Intro", order=1),
    _p("guides/a.md", "A", order=1),
    _p("guides/deep/b.md", "B"),
    _p("ref/c.md", "C"),
]


def _setup() -> tuple[list[Page], Any]:
    pages = [Page(**{**p.__dict__}) for p in PAGES]
    assign_routes(pages, "/repo")
    return pages, build_tree(pages)


def test_menu_structure() -> None:
    _, tree = _setup()
    menu = build_menu(tree, "/guides/deep/b/")
    assert [g.get("label") for g in menu] == [None, "Guides", "Ref"]
    assert [i["label"] for i in menu[0]["items"]] == ["Home", "About"]

    guides = menu[1]["items"]
    assert [i["type"] for i in guides] == ["item", "item", "submenu"]
    assert guides[0]["label"] == "Intro"  # folder index item uses sidebar.label
    assert guides[0]["url"] == "/repo/guides/"
    assert guides[2]["label"] == "Deep"

    ref = menu[2]["items"]
    assert [i["label"] for i in ref] == ["C"]  # no index page, no Overview item


def test_current_and_open_flags() -> None:
    _, tree = _setup()
    menu = build_menu(tree, "/guides/deep/b/")
    deep = menu[1]["items"][2]
    assert deep["open"] is True
    assert deep["items"][0]["current"] is True
    flat = [menu[0]["items"], menu[1]["items"][:2], menu[2]["items"]]
    assert not any(i["current"] for items in flat for i in items)

    menu = build_menu(tree, "/about/")
    assert menu[1]["items"][2]["open"] is False
    assert menu[0]["items"][1]["current"] is True


def test_index_item_defaults_to_overview() -> None:
    pages = [_p("g/index.md", "G"), _p("g/x.md")]
    assign_routes(pages, "")
    menu = build_menu(build_tree(pages), "/")
    assert menu[0]["items"][0]["label"] == "Overview"


def test_labels_escaped_once() -> None:
    evil = "<script>alert(1)</script> & co"
    pages = [
        _p("a.md", evil),
        _p("evil/index.md", evil),
        _p("evil/x.md"),
        _p("evil/sub/y.md", evil),
        _p("evil/sub/index.md", evil, badge={"text": "<b>", "variant": '"x'}),
    ]
    assign_routes(pages, "")
    menu = build_menu(build_tree(pages), "/")
    item = menu[0]["items"][0]["label"]
    assert item == "&lt;script&gt;alert(1)&lt;/script&gt; &amp; co"
    submenu = menu[1]["items"][1]
    assert submenu["type"] == "submenu" and "<script>" not in submenu["label"]
    assert (
        '<span class="badge" data-variant="&quot;x">&lt;b&gt;</span>'
        in submenu["items"][0]["label"]
    )
    # Group labels are escaped by the macro, so they stay raw here.
    assert menu[1]["label"] == evil


def test_badge_string() -> None:
    pages = [_p("a.md", "A", badge="New")]
    assign_routes(pages, "")
    label = build_menu(build_tree(pages), "/")[0]["items"][0]["label"]
    assert label == 'A <span class="badge" data-variant="secondary">New</span>'


def test_prev_next_follows_menu_order() -> None:
    pages, tree = _setup()
    order = ordered_pages(tree)
    assert [p.title for p in order] == ["Home", "About", "Guides", "A", "B", "C"]
    by_title = {p.title: p for p in pages}
    prev, nxt = prev_next(order, by_title["A"])
    assert prev and nxt and (prev.title, nxt.title) == ("Guides", "B")
    assert prev_next(order, by_title["Home"])[0] is None
    assert prev_next(order, by_title["C"])[1] is None


def test_breadcrumbs() -> None:
    pages, _ = _setup()
    index = {p.rel.parent: p for p in pages if p.rel.stem == "index"}
    by_title = {p.title: p for p in pages}
    crumbs = breadcrumbs(by_title["B"], index)
    assert [(c.label, c.url) for c in crumbs] == [
        ("Guides", "/repo/guides/"),
        ("Deep", None),
        ("B", None),
    ]
    assert [c.label for c in breadcrumbs(by_title["Guides"], index)] == ["Guides"]
    assert [c.label for c in breadcrumbs(by_title["Home"], index)] == ["Home"]
