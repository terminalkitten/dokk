from pathlib import Path

import pytest

from dokk.content import ContentError, load_page, scan, titleize


def _page(tmp_path: Path, rel: str, text: str):
    src = tmp_path / rel
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(text, encoding="utf-8")
    return load_page(src, tmp_path)


def test_front_matter(tmp_path: Path) -> None:
    p = _page(tmp_path, "a.md", "---\ntitle: A\ndescription: D\n---\n\nBody\n")
    assert (p.title, p.description, p.body.strip()) == ("A", "D", "Body")
    assert p.rel == Path("a.md")


def test_title_from_h1_is_removed_from_body(tmp_path: Path) -> None:
    p = _page(tmp_path, "a.md", "\n# Hello *there*\n\nText\n")
    assert p.title == "Hello *there*"
    assert p.body.strip() == "Text"


def test_title_from_filename(tmp_path: Path) -> None:
    assert _page(tmp_path, "my_cool-page.md", "Text").title == "My Cool Page"
    assert _page(tmp_path, "some-dir/index.md", "Text").title == "Some Dir"
    assert _page(tmp_path, "index.md", "Text").title == "Home"


def test_titleize() -> None:
    assert titleize("getting-started") == "Getting Started"
    assert titleize("café_ünïcode") == "Café Ünïcode"


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("---\ntitle: [\n---\n", "invalid front matter"),
        ("---\n- a\n---\n", "must be a mapping"),
        ("---\nsidebar: x\n---\n", "'sidebar' must be a mapping"),
        ("---\nsidebar:\n  order: first\n---\n", "'sidebar.order' must be a number"),
    ],
)
def test_front_matter_errors(tmp_path: Path, text: str, message: str) -> None:
    with pytest.raises(ContentError, match="a.md") as exc:
        _page(tmp_path, "a.md", text)
    assert message in str(exc.value)


def test_scan_skips_drafts(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("A")
    (tmp_path / "b.md").write_text("---\ndraft: true\n---\nB")
    (tmp_path / "c.txt").write_text("not markdown")
    assert [p.rel.name for p in scan(tmp_path)] == ["a.md"]
    assert [p.rel.name for p in scan(tmp_path, drafts=True)] == ["a.md", "b.md"]


def test_line_offset(tmp_path: Path) -> None:
    assert _page(tmp_path, "a.md", "---\ntitle: A\n---\nBody\n").line_offset == 3
    assert _page(tmp_path, "b.md", "# Title\n\nBody\n").line_offset == 1
    assert _page(tmp_path, "c.md", "Body\n").line_offset == 0
