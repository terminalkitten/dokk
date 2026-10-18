import os
import re
from pathlib import Path

import pytest

from dokk.markdown import Renderer, TocItem, _truncate, highlight_code, pygments_css
from dokk.render import base_env

GOLDEN = Path(__file__).parent / "golden"
EXAMPLE_DOCS = Path(__file__).resolve().parents[1] / "examples" / "basic" / "docs"


def _normalize(html: str) -> str:
    return re.sub(r"\s+", " ", html).strip()


@pytest.fixture
def content(tmp_path: Path) -> Path:
    (tmp_path / "guides" / "img").mkdir(parents=True)
    (tmp_path / "guides" / "img" / "pic one.png").write_bytes(b"png")
    (tmp_path / "file.pdf").write_bytes(b"pdf")
    return tmp_path


def _renderer(content: Path, base: str = "") -> Renderer:
    urls = {
        "index.md": f"{base}/",
        "guides/intro.md": f"{base}/guides/intro/",
        "guides/index.md": f"{base}/guides/",
    }
    return Renderer(urls, content, base, base_env())


def _hrefs(html: str) -> list[str]:
    return re.findall(r'(?:href|src)="([^"]*)"', html)


def test_golden_rich_page() -> None:
    src = EXAMPLE_DOCS / "guides" / "markdown.md"
    body = src.read_text(encoding="utf-8").split("---", 2)[2]
    urls = {
        "getting-started/install.md": "/repo/getting-started/install/",
        "index.md": "/repo/",
    }
    html = (
        Renderer(urls, EXAMPLE_DOCS, "/repo", base_env())
        .render(body, Path("guides/markdown.md"))
        .html
    )
    golden = GOLDEN / "markdown.html"
    if os.environ.get("DOKK_UPDATE_GOLDEN"):
        golden.parent.mkdir(exist_ok=True)
        golden.write_text(html, encoding="utf-8")
    assert _normalize(html) == _normalize(golden.read_text(encoding="utf-8"))


@pytest.mark.parametrize("base", ["", "/repo"])
def test_link_rewriting(content: Path, base: str) -> None:
    body = (
        "[a](intro.md) [b](../index.md#top) [c](index.md) [d](./intro.md#x-y)\n"
        "[e](/abs/) [f](https://x.io/a.md) [g](#local) [h](mailto:a@b.c)\n"
        "[i](../file.pdf) ![j](img/pic%20one.png) ![k](./img/pic one.png)\n"
    ).replace("![k](./img/pic one.png)", "![k](<./img/pic one.png>)")
    result = _renderer(content, base).render(body, Path("guides/intro.md"))
    assert result.broken == []
    assert _hrefs(result.html) == [
        f"{base}/guides/intro/",
        f"{base}/#top",
        f"{base}/guides/",
        f"{base}/guides/intro/#x-y",
        f"{base}/abs/",
        "https://x.io/a.md",
        "#local",
        "mailto:a@b.c",
        f"{base}/file.pdf",
        f"{base}/guides/img/pic%20one.png",
        f"{base}/guides/img/pic%20one.png",
    ]


def test_root_absolute_link_not_prefixed_twice(content: Path) -> None:
    html = _renderer(content, "/repo").render("[a](/repo/x/) [b](/repo)", Path("index.md")).html
    assert _hrefs(html) == ["/repo/x/", "/repo"]


def test_broken_links_are_recorded_and_left_alone(content: Path) -> None:
    body = "[a](missing.md) ![b](nope.png) [c](../../outside.md) [d](sub/)"
    result = _renderer(content).render(body, Path("guides/intro.md"))
    assert result.broken == ["missing.md", "nope.png", "../../outside.md", "sub/"]
    assert _hrefs(result.html) == result.broken


def test_toc_and_permalinks(content: Path) -> None:
    body = "# Title\n\n## One `code` *em*\n\n### Two\n\n#### Four\n\n## One `code` *em*\n"
    result = _renderer(content).render(body, Path("index.md"))
    assert result.toc == [
        TocItem(2, "one-code-em", "One code em"),
        TocItem(3, "two", "Two"),
        TocItem(2, "one-code-em-1", "One code em"),
    ]
    assert '<a class="header-anchor" href="#two">#</a>' in result.html
    assert "<h1>Title</h1>" in result.html  # H1 gets no id or permalink


def test_toc_text_is_escaped_by_template_not_here(content: Path) -> None:
    result = _renderer(content).render("## a &lt;b&gt; <i>c</i>\n", Path("index.md"))
    assert result.toc[0].text == "a <b> c"


def test_description_fallback(content: Path) -> None:
    body = "## Heading\n\nFirst *para*\nline two.\n\nSecond.\n"
    assert _renderer(content).render(body, Path("index.md")).description == "First para line two."


def test_truncate() -> None:
    text = "word " * 50
    out = _truncate(text, 20)
    assert out == "word word word word…" and len(out) <= 20
    assert _truncate("short") == "short"


def test_highlight() -> None:
    html = highlight_code("x = 1\n", "python", "")
    assert html.startswith('<pre class="code hl"><code class="language-python">')
    assert '<span class="n">x</span>' in html
    assert 'class="language-text"' in highlight_code("x", "", "")
    assert "<span" not in highlight_code("x <y>", "nosuchlang", "")
    assert 'class="language-&#34;x"' in highlight_code("x", '"x', "")
    assert type(highlight_code("x", "", "")) is str  # not Markup: see highlight_code


def test_table_wrapped(content: Path) -> None:
    html = _renderer(content).render("|a|\n|-|\n|1|\n", Path("index.md")).html
    assert '<div class="table-container"><table class="table">' in html


def test_pygments_css_is_scoped() -> None:
    css = pygments_css("default", "github-dark").splitlines()
    assert css and all(
        line.startswith(("html:not(.dark) .dk-prose .hl", "html.dark .dk-prose .hl"))
        for line in css
    )
    assert any(line.startswith("html.dark .dk-prose .hl .k ") for line in css)
    assert not any("/*" in line for line in css)


def test_task_list_checkboxes_are_labelled(content: Path) -> None:
    html = _renderer(content).render("- [x] done\n", Path("index.md")).html
    assert "<label><input" in html and "done</label>" in html
