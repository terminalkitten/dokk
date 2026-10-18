from pathlib import Path
from typing import Any

import pytest

from dokk.content import Page
from dokk.menu import (
    NavError,
    Pager,
    auto_nav,
    breadcrumbs,
    build_menu,
    config_nav,
    mark_current,
    ordered_pages,
    submenu_keys,
)
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


def _pages() -> list[Page]:
    pages = [
        _p("index.md", "Home"),
        _p("about.md", "About"),
        _p("guides/index.md", "Guides", label="Intro", order=1),
        _p("guides/a.md", "A", order=1),
        _p("guides/deep/b.md", "B"),
        _p("ref/c.md", "C"),
    ]
    assign_routes(pages, "/repo")
    return pages


def test_auto_menu_structure() -> None:
    pages = _pages()
    nav = auto_nav(build_tree(pages))
    menu = build_menu(nav)
    assert [g.get("label") for g in menu] == ["", "Guides", "Ref"]
    assert [i["label"] for i in menu[0]["items"]] == ["Home", "About"]
    guides = menu[1]["items"]
    assert [i["type"] for i in guides] == ["item", "item", "submenu"]
    assert guides[0]["label"] == "Intro"  # folder index item uses sidebar.label
    assert guides[0]["url"] == "/repo/guides/"
    assert guides[2]["label"] == "Deep"
    assert [i["label"] for i in menu[2]["items"]] == ["C"]  # no index page, no Overview item


def test_submenu_keys() -> None:
    pages = _pages()
    nav = auto_nav(build_tree(pages))
    keys, around = submenu_keys(nav)
    by_title = {p.title: p for p in pages}
    assert build_menu(nav, keys)[1]["items"][2]["attrs"] == {"data-sub": "1"}
    assert around[id(by_title["B"])] == ("1",)
    assert around[id(by_title["About"])] == ()


def test_mark_current_opens_submenus() -> None:
    html = '<details data-sub="1"><details data-sub="12"><details data-sub="2">'
    assert mark_current(html, "/x/", ("1", "2")) == (
        '<details open data-sub="1"><details data-sub="12"><details open data-sub="2">'
    )


def test_mark_current() -> None:
    html = (
        '<a class="dk-brand" href="/x/">t</a><a href="/x/" ><span>X</span></a><a href="/x/">dup</a>'
    )
    out = mark_current(html, "/x/")
    assert out.count('aria-current="page"') == 1
    assert '<a href="/x/" aria-current="page" >' in out  # the menu link, not the brand link


def test_index_item_defaults_to_overview() -> None:
    pages = [_p("g/index.md", "G"), _p("g/x.md")]
    assign_routes(pages, "")
    menu = build_menu(auto_nav(build_tree(pages)))
    assert menu[0]["items"][0]["label"] == "Overview"


def test_labels_escaped_once() -> None:
    evil = "<script>alert(1)</script> & co"
    pages = [
        _p("a.md", evil),
        _p("evil/index.md", evil),
        _p("evil/x.md"),
        _p("evil/sub/y.md", evil),
        _p("evil/sub/index.md", evil, badge={"text": "<b>", "variant": "danger"}),
    ]
    assign_routes(pages, "")
    menu = build_menu(auto_nav(build_tree(pages)))
    assert menu[0]["items"][0]["label"] == "&lt;script&gt;alert(1)&lt;/script&gt; &amp; co"
    submenu = menu[1]["items"][1]
    assert submenu["type"] == "submenu" and "<script>" not in submenu["label"]
    badge = '<span class="badge" data-variant="destructive">&lt;b&gt;</span>'
    assert badge in submenu["items"][0]["label"]
    assert menu[1]["label"] == evil  # group labels are escaped by the macro


def test_badge_string() -> None:
    pages = [_p("a.md", "A", badge="New")]
    assign_routes(pages, "")
    label = build_menu(auto_nav(build_tree(pages)))[0]["items"][0]["label"]
    assert label == 'A <span class="badge" data-variant="secondary">New</span>'


def test_badge_variant_checked() -> None:
    pages = [_p("a.md", "A", badge={"text": "X", "variant": '"x'})]
    assign_routes(pages, "")
    with pytest.raises(NavError, match="a.md: sidebar.badge 'X': variant must be one of default"):
        build_menu(auto_nav(build_tree(pages)))


def test_pager_follows_menu_order() -> None:
    pages = _pages()
    order = ordered_pages(auto_nav(build_tree(pages)))
    assert [p.title for p in order] == ["Home", "About", "Guides", "A", "B", "C"]
    pager, by_title = Pager(order), {p.title: p for p in pages}
    prev, nxt = pager(by_title["A"])
    assert prev and nxt and (prev.title, nxt.title) == ("Guides", "B")
    assert pager(by_title["Home"])[0] is None and pager(by_title["C"])[1] is None
    assert pager(_p("other.md")) == (None, None)


def test_breadcrumbs() -> None:
    pages = _pages()
    index = {p.rel.parent: p for p in pages if p.rel.stem == "index"}
    by_title = {p.title: p for p in pages}
    assert [(c.label, c.url) for c in breadcrumbs(by_title["B"], index)] == [
        ("Guides", "/repo/guides/"),
        ("Deep", None),
        ("B", None),
    ]
    assert [c.label for c in breadcrumbs(by_title["Guides"], index)] == ["Guides"]


# [[sidebar]] from dokk.toml


def _config(entries: list[Any], tmp_path: Path = Path("/nonexistent")):  # type: ignore[no-untyped-def]
    pages = _pages()
    by_rel = {p.rel.as_posix(): p for p in pages}
    return config_nav(entries, build_tree(pages), by_rel, tmp_path, "/repo")


def test_config_mixes_pages_autogenerate_and_links() -> None:
    nav = _config(
        [
            {"label": "Start", "items": ["index.md", {"page": "about.md", "label": "Who"}]},
            {"label": "Guides", "autogenerate": "guides"},
            {"label": "More", "items": [
                {"label": "GitHub", "link": "https://github.com/x"},
                {"label": "Changelog", "link": "/changes/"},
                {"label": "Sub", "items": ["ref/c.md"]},
            ]},
            "about.md",
        ]
    )  # fmt: skip
    menu = build_menu(nav)
    assert [g.get("label") for g in menu] == ["Start", "Guides", "More", None]
    assert [(i["label"], i["url"]) for i in menu[0]["items"]] == [
        ("Home", "/repo/"),
        ("Who", "/repo/about/"),
    ]
    assert [i["label"] for i in menu[1]["items"]] == ["Intro", "A", "Deep"]
    more = menu[2]["items"]
    assert (more[0]["url"], more[1]["url"]) == ("https://github.com/x", "/repo/changes/")
    assert more[2]["type"] == "submenu" and more[2]["items"][0]["label"] == "C"
    assert menu[3]["items"][0]["label"] == "About"  # loose top-level page
    titles = [p.title for p in ordered_pages(nav)]
    assert titles == ["Home", "About", "Guides", "A", "B", "C"]  # first occurrence wins


def test_config_autogenerate_label_defaults_to_folder() -> None:
    assert build_menu(_config([{"autogenerate": "guides"}]))[0]["label"] == "Guides"


@pytest.mark.parametrize(
    ("entry", "message"),
    [
        ("missing.md", "page 'missing.md' not found"),
        ({"autogenerate": "nope"}, "folder 'nope' not found"),
        ({"link": "https://x"}, "needs a label"),
        ({"label": "x"}, "needs page, link, autogenerate or items"),
        (3, "unexpected entry 3"),
    ],
)
def test_config_errors(entry: Any, message: str) -> None:
    with pytest.raises(NavError, match="dokk.toml: sidebar") as exc:
        _config([entry])
    assert message in str(exc.value)


def test_config_skips_drafts(tmp_path: Path) -> None:
    (tmp_path / "wip.md").write_text("---\ndraft: true\n---\n")
    assert _config(["wip.md", "about.md"], tmp_path)[0].page.title == "About"
