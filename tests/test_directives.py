import re
from pathlib import Path

import pytest

from dokk.directives import Directive, DirectiveError, parse_info
from dokk.markdown import Renderer
from dokk.render import base_env


@pytest.mark.parametrize(
    ("info", "expected"),
    [
        ("note", Directive("note")),
        ("note[My title]", Directive("note", "My title")),
        (
            ' card[Go]{href="/x/" class="y"} ',
            Directive("card", "Go", {"href": "/x/", "class": "y"}),
        ),
        ("tab[]", Directive("tab")),
        ("note [not a title]", None),
        ("1note", None),
        ("", None),
    ],
)
def test_parse_info(info: str, expected: Directive | None) -> None:
    assert parse_info(info) == expected


@pytest.fixture
def renderer(tmp_path: Path) -> Renderer:
    urls = {"index.md": "/repo/", "guide.md": "/repo/guide/"}
    return Renderer(urls, tmp_path, "/repo", base_env())


def _render(renderer: Renderer, body: str, line_offset: int = 0) -> str:
    return renderer.render(body, Path("page.md"), line_offset).html


def test_callouts(renderer: Renderer) -> None:
    html = _render(renderer, ":::tip\nUse **bold** and [a link](guide.md).\n:::\n")
    assert 'class="alert dk-callout" role="note" data-callout="tip"' in html
    assert "<strong>Tip</strong>" in html
    assert "<strong>bold</strong>" in html
    assert 'href="/repo/guide/"' in html
    assert ":::" not in html


def test_callout_title_escaped(renderer: Renderer) -> None:
    html = _render(renderer, ":::danger[<script>x</script> & co]\nBody\n:::\n")
    assert "<strong>&lt;script&gt;x&lt;/script&gt; &amp; co</strong>" in html
    assert "<script>" not in html


def test_tabs_have_stable_ids_and_escaped_labels(renderer: Renderer) -> None:
    body = (
        "::::tabs\n:::tab[<b>One</b>]\nFirst\n:::\n:::tab\nSecond\n:::\n::::\n\n"
        "::::tabs\n:::tab[A]\nx\n:::\n::::\n"
    )
    html = _render(renderer, body)
    assert re.findall(r'class="tabs dk-tabs"\s+id="([^"]+)"', html) == ["dk-tabs-1", "dk-tabs-2"]
    assert "&lt;b&gt;One&lt;/b&gt;" in html and "<b>One</b>" not in html
    assert re.search(r'role="tab"[^>]*>\s*Tab 2\s*</button>', html)  # default label
    assert "<p>First</p>" in html and "<p>Second</p>" in html
    assert _render(renderer, body) == html  # same input, same ids


def test_nested_directives(renderer: Renderer) -> None:
    body = "::::::tabs\n:::::tab[A]\n::::note\nInner *md*\n::::\n:::::\n::::::\n"
    html = _render(renderer, body)
    assert 'data-callout="note"' in html and "<em>md</em>" in html
    assert html.index('role="tabpanel"') < html.index('data-callout="note"')


def test_headings_inside_directives_are_in_toc(renderer: Renderer) -> None:
    result = renderer.render(":::note\n## Inside\n:::\n", Path("page.md"))
    assert [t.id for t in result.toc] == ["inside"]
    assert 'id="inside"' in result.html


def test_cards_and_href_rewriting(renderer: Renderer) -> None:
    body = (
        '::::cards\n:::card[Guide]{href="guide.md#x"}\nText\n:::\n'
        ':::card[Abs]{href="/abs/"}\nText\n:::\n:::card[Plain]\nText\n:::\n::::\n'
    )
    result = renderer.render(body, Path("page.md"))
    assert result.html.startswith('<div class="dk-cards">')
    assert re.findall(r'class="card-title dk-card-link" href="([^"]+)"', result.html) == [
        "/repo/guide/#x",
        "/repo/abs/",
    ]
    assert '<strong class="card-title">Plain</strong>' in result.html
    assert result.broken == []


def test_broken_card_href_is_recorded(renderer: Renderer) -> None:
    result = renderer.render(':::card[X]{href="missing.md"}\nText\n:::\n', Path("page.md"))
    assert result.broken == ["missing.md"]


def test_steps(renderer: Renderer) -> None:
    html = _render(renderer, ":::steps\n1. One\n2. Two\n:::\n")
    assert html.startswith('<div class="dk-steps"><ol>')


def test_code_fence_is_not_a_directive(renderer: Renderer) -> None:
    html = _render(renderer, "```\n:::note\n:::\n```\n")
    assert ":::note" in html and "dk-callout" not in html


@pytest.mark.parametrize(
    ("body", "message"),
    [
        ("text\n\n:::bogus\nx\n:::\n", "page.md: line 12: unknown directive ':::bogus'"),
        (":::tab[A]\nx\n:::\n", "page.md: line 10: ':::tab' must be inside '::::tabs'"),
        ("::::tabs\nloose text\n::::\n", "'::::tabs' may only contain ':::tab' blocks"),
    ],
)
def test_errors_cite_file_and_line(renderer: Renderer, body: str, message: str) -> None:
    with pytest.raises(DirectiveError) as exc:
        _render(renderer, body, line_offset=9)
    assert message in str(exc.value)


def test_component_template_override(tmp_path: Path) -> None:
    user = tmp_path / "templates" / "components"
    user.mkdir(parents=True)
    (user / "steps.html.jinja").write_text("<ol class='mine'>{{ body }}</ol>")
    r = Renderer({}, tmp_path, "", base_env(tmp_path / "templates"))
    assert r.render(":::steps\n1. A\n:::\n", Path("p.md")).html.startswith("<ol class='mine'>")
