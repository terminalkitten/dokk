import re
from pathlib import Path

import pytest

from dokk.directives import Directive, DirectiveError, parse_attrs, parse_info
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
    (user / "steps.html.jinja").write_text("<ol class='mine'>{{ body }}</ol>", encoding="utf-8")
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


def test_inline_kbd_and_swatch(renderer: Renderer) -> None:
    html = _render(
        renderer, "Press :kbd[Ctrl+K] or :kbd[<x>]. Pink :swatch[oklch(0.65 0.24 354)].\n"
    )
    assert '<kbd class="kbd">Ctrl+K</kbd>' in html
    assert '<kbd class="kbd">&lt;x&gt;</kbd>' in html
    color = "oklch(0.65 0.24 354)"
    assert (
        f'<span class="dk-swatch" style="--dk-swatch: {color}" role="img" '
        f'aria-label="{color}" title="{color}"></span>'
    ) in html


@pytest.mark.parametrize("color", ["red;background:url(x)", 'red" onclick="x', ""])
def test_swatch_rejects_non_colors(renderer: Renderer, color: str) -> None:
    with pytest.raises(DirectiveError, match="not a CSS color"):
        _render(renderer, f":swatch[{color}]\n")


def test_image(renderer: Renderer) -> None:
    (renderer.content_dir / "img").mkdir()
    (renderer.content_dir / "img" / "a.png").write_bytes(b"")
    html = _render(
        renderer,
        '::image[A <chart>]{src="img/a.png" width="640" height="400" caption="Sales"}\n\n'
        ':::image[Second]{src="img/a.png"}\nWith a **caption**.\n:::\n',
    )
    assert (
        '<a href="/repo/img/a.png" class="dk-image-zoom" data-dk-zoom '
        'aria-label="Enlarge image: A &lt;chart&gt;">'
    ) in html
    assert (
        '<img src="/repo/img/a.png" alt="A &lt;chart&gt;" loading="lazy" decoding="async" '
        'width="640" height="400">'
    ) in html
    assert "<figcaption>Sales</figcaption>" in html
    assert "<figcaption><p>With a <strong>caption</strong>.</p>\n</figcaption>" in html


def test_image_errors(renderer: Renderer) -> None:
    with pytest.raises(DirectiveError, match=r"page.md: line 1: use ::image\[Alt text\]"):
        _render(renderer, '::image{src="img/a.png"}\n')
    result = renderer.render('::image[Gone]{src="img/gone.png"}\n', Path("page.md"))
    assert result.broken == ["img/gone.png"]


def test_model(renderer: Renderer) -> None:
    html = _render(
        renderer,
        ':::model[Acme <Large>]{provider="Acme" model="acme-l" input="3" output="€15" '
        'context="200K" features="vision tools custom" href="guide.md"}\n'
        "The **best** one.\n:::\n\n"
        "::model[Bare]\n",
    )
    assert '<strong class="card-title">Acme &lt;Large&gt;</strong>' in html
    assert "Acme · <code>acme-l</code>" in html
    assert "<dd>$3 / 1M</dd>" in html
    assert "<dd>€15 / 1M</dd>" in html  # a currency is kept
    assert "<dd>200K</dd>" in html
    assert "Cached input" not in html  # only what is given
    assert "<p>The <strong>best</strong> one.</p>" in html
    assert html.count("<svg") == html.count("</svg>")
    assert re.search(r"<svg[^>]*>.*?</svg>vision</span>", html)  # a known feature has an icon
    assert re.search(r'secondary">\s*custom</span>', html)  # an unknown one has none
    assert 'href="/repo/guide/"' in html
    assert 'id="dk-model-2"' in html  # the one-line card
    with pytest.raises(DirectiveError, match=r"line 1: use ::model\[Name\]"):
        _render(renderer, '::model{input="1"}\n')


def test_huggingface(renderer: Renderer) -> None:
    html = _render(renderer, '::huggingface[meta-llama/Llama-3.1-8B]{params="8B"}\n')
    assert 'href="https://huggingface.co/meta-llama/Llama-3.1-8B"' in html
    assert '<span class="dk-hf-owner">meta-llama/</span>Llama-3.1-8B' in html
    assert "Hugging Face model" in html
    assert "</svg>8B</span>" in html
    html = _render(renderer, ':::huggingface[org/data]{type="dataset"}\nAbout it.\n:::\n')
    assert 'href="https://huggingface.co/datasets/org/data"' in html
    assert "<section><p>About it.</p>" in html
    with pytest.raises(DirectiveError, match="type must be one of model, dataset, space"):
        _render(renderer, '::huggingface[a/b]{type="repo"}\n')


def test_prompt(renderer: Renderer) -> None:
    html = _render(
        renderer,
        '- before\n\n:::prompt[Review]{role="system"}\nYou are "careful".\n\n1. Bugs first\n:::\n',
    )
    # The Markdown as written, for Copy and the Open links.
    assert 'data-dk-prompt="You are &#34;careful&#34;.\n\n1. Bugs first"' in html
    assert '<div class="dk-prompt-text"><p>You are' in html
    assert "<footer hidden>" in html
    assert html.count("data-dk-prompt-open=") == 2
    html = _render(renderer, ':::prompt{open="false"}\nHi\n:::\n')
    assert "data-dk-prompt-open" not in html
    assert '<strong class="card-title">Prompt</strong>' in html


def test_model_and_huggingface_logos(renderer: Renderer) -> None:
    html = _render(renderer, '::model[Claude]{icon="claude"}\n\n::huggingface[a/b]\n')
    logo = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
    assert f'<span class="dk-model-avatar">{logo}fill="currentColor" class="dk-vendor-logo"' in html
    assert f'<span class="dk-hf-logo">{logo}' in html
    assert html.count('class="dk-vendor-logo"') == 2  # only the logos the page uses
    with pytest.raises(DirectiveError, match='unknown icon "acme"; choose from anthropic, '):
        _render(renderer, '::model[X]{icon="acme"}\n')


def test_attribute_values_without_quotes() -> None:
    assert parse_attrs('dev=true tools="uv pip" max=100') == {
        "dev": "true",
        "tools": "uv pip",
        "max": "100",
    }
