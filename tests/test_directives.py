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


FILE_TREE = """:::filetree
- astro.config.mjs
- **README.md** an *important* file
- src
  - components
    - Header.astro
    - …
  - pages/
- `Hello world.txt`
:::
"""


def test_file_tree_structure() -> None:
    from markdown_it import MarkdownIt

    from dokk.filetree import file_tree

    md = MarkdownIt("commonmark")
    entries = file_tree(md.parse("- a\n- b/\n- c\n  - d\n  - ...\n"), lambda t: "")
    assert [(e.name, e.is_dir) for e in entries] == [("a", False), ("b/", True), ("c", True)]
    assert [e.name for e in entries[2].children] == ["d", "..."]
    assert entries[2].children[1].placeholder


def test_file_tree_html(renderer: Renderer) -> None:
    html = _render(renderer, FILE_TREE)
    assert html.startswith('<div class="dk-filetree">')
    assert '<li class="dk-ft-highlight"><span class="dk-ft-entry">' in html
    assert '<span class="dk-ft-comment">an <em>important</em> file</span>' in html
    assert "<details open><summary><svg" in html and '<span class="dk-ft-name">src</span>' in html
    assert '<span class="dk-ft-entry"><span class="dk-ft-name">…</span>' in html  # no icon
    assert '<span class="dk-ft-name">Hello world.txt</span>' in html
    assert '<span class="dk-ft-name">pages/</span>' in html


def test_file_tree_needs_a_list(renderer: Renderer) -> None:
    with pytest.raises(
        DirectiveError, match="line 1: a file tree may only contain a bulleted list"
    ):
        _render(renderer, ":::filetree\nJust text.\n:::\n")


def test_link_buttons(renderer: Renderer) -> None:
    body = (
        '::linkbutton[Start]{href="guide.md"}\n'
        '::linkbutton[Astro]{href="https://astro.build" variant="secondary"}\n'
        '::linkbutton[More]{href="/more/" variant="minimal"}\n'
    )
    html = _render(renderer, body)
    assert '<a class="btn dk-linkbutton" href="/repo/guide/">Start</a>' in html
    assert 'href="https://astro.build" data-variant="outline">Astro<svg' in html  # external icon
    assert 'href="/repo/more/" data-variant="ghost">More</a>' in html
    assert "<p>" not in html  # each button is its own block, not a paragraph


@pytest.mark.parametrize(
    ("body", "message"),
    [
        ('::linkbutton{href="/x/"}\n', "use ::linkbutton[Text]"),
        ("::linkbutton[Go]\n", "use ::linkbutton[Text]"),
        ('::linkbutton[Go]{href="/x/" variant="big"}\n', "variant must be one of"),
        ("::bogus[x]\n", "unknown directive"),
    ],
)
def test_leaf_errors(renderer: Renderer, body: str, message: str) -> None:
    with pytest.raises(DirectiveError, match="line 1") as exc:
        _render(renderer, body)
    assert message in str(exc.value)


def test_leaf_syntax_only_on_its_own_line(renderer: Renderer) -> None:
    html = _render(
        renderer, 'Text ::linkbutton[x]{href="/"}\n\n```\n::linkbutton[y]{href="/"}\n```\n'
    )
    assert "dk-linkbutton" not in html
    assert _render(renderer, "a::b and :: and ::: alone\n").startswith("<p>")


def test_broken_linkbutton_href_is_recorded(renderer: Renderer) -> None:
    result = renderer.render('::linkbutton[Go]{href="missing.md"}\n', Path("page.md"))
    assert result.broken == ["missing.md"]


def test_code_block_title_and_highlighted_lines(renderer: Renderer) -> None:
    html = _render(renderer, '```py title="app.py" {2,4-5}\na\nb\nc\nd\ne\n```\n')
    assert html.startswith('<figure class="dk-codeblock"><figcaption>app.py</figcaption><pre')
    assert html.count('<span class="hll">') == 3
    plain = _render(renderer, "```py\nx\n```\n")
    assert plain.startswith('<pre class="code hl">') and "hll" not in plain


def test_code_block_title_escaped(renderer: Renderer) -> None:
    html = _render(renderer, '```sh title="<b>x</b>"\nls\n```\n')
    assert "<figcaption>&lt;b&gt;x&lt;/b&gt;</figcaption>" in html


def test_details(renderer: Renderer) -> None:
    html = _render(renderer, ":::details[More]\nHidden *text*.\n:::\n\n:::details\nx\n:::\n")
    assert '<details class="dk-details">\n  <summary>More</summary>' in html
    assert "<em>text</em>" in html and "<summary>Details</summary>" in html


def test_inline_badges(renderer: Renderer) -> None:
    html = _render(
        renderer,
        'A :badge[New] b :badge[Beta]{variant="secondary"} :badge[<x>]{variant="danger"} '
        "a:b[c] ::badge[x] `:badge[code]`\n",
    )
    assert '<span class="badge">New</span>' in html
    assert '<span class="badge" data-variant="secondary">Beta</span>' in html
    assert '<span class="badge" data-variant="destructive">&lt;x&gt;</span>' in html
    assert "a:b[c] ::badge[x] <code>:badge[code]</code>" in html


def test_badge_bad_variant(renderer: Renderer) -> None:
    with pytest.raises(DirectiveError, match="page.md: badge 'x': variant must be one of"):
        _render(renderer, ':badge[x]{variant="huge"}\n')


def test_synced_tabs(renderer: Renderer) -> None:
    html = _render(renderer, '::::tabs{sync="pkg"}\n:::tab[pip]\nx\n:::\n::::\n')
    assert 'data-sync="pkg"' in html
    assert "data-sync" not in _render(renderer, "::::tabs\n:::tab[pip]\nx\n:::\n::::\n")
