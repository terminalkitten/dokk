import unicodedata
from pathlib import Path

import pytest

from dokk.content import Page
from dokk.routes import RouteError, assign_routes, output_path, route_for, slugify


@pytest.mark.parametrize(
    ("segment", "slug"),
    [
        ("Getting Started", "getting-started"),
        ("snake_case_name", "snake-case-name"),
        ("a  --  b", "a-b"),
        ("Hello, World!", "hello-world"),
        ("café-ünïcode", "café-ünïcode"),
        (unicodedata.normalize("NFD", "café"), "café"),  # macOS file names
        ("日本語", "日本語"),
        ("v1.2", "v12"),
        ("-edge-", "edge"),
    ],
)
def test_slugify(segment: str, slug: str) -> None:
    assert slugify(segment) == slug


@pytest.mark.parametrize(
    ("rel", "route", "out"),
    [
        ("index.md", "/", "index.html"),
        ("guides/index.md", "/guides/", "guides/index.html"),
        ("guides/intro.md", "/guides/intro/", "guides/intro/index.html"),
        ("Getting Started.md", "/getting-started/", "getting-started/index.html"),
        ("A B/C_D.md", "/a-b/c-d/", "a-b/c-d/index.html"),
    ],
)
def test_route_mapping(rel: str, route: str, out: str) -> None:
    assert route_for(Path(rel)) == route
    assert output_path(route) == Path(out)


def test_empty_slug_is_an_error() -> None:
    with pytest.raises(RouteError, match="empty slug"):
        route_for(Path("!!!.md"))


def _p(rel: str) -> Page:
    return Page(src=Path("/x") / rel, rel=Path(rel), meta={}, body="")


def test_collision_names_both_files() -> None:
    with pytest.raises(RouteError) as exc:
        assign_routes([_p("Getting Started.md"), _p("getting-started.md")], "")
    msg = str(exc.value)
    assert "Getting Started.md" in msg and "getting-started.md" in msg


def test_base_path_prefixes_url_not_route() -> None:
    pages = [_p("index.md"), _p("guides/intro.md")]
    assign_routes(pages, "/repo")
    assert [(p.route, p.url) for p in pages] == [
        ("/", "/repo/"),
        ("/guides/intro/", "/repo/guides/intro/"),
    ]
