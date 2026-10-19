from pathlib import Path

from dokk.cli import main
from dokk.formatter import format_docs

MESSY = """---
title: Page
---

:::steps
1. One
2. Two
:::

* a
* b

:::env
KEY=        # Aligned.
OTHER=1     # Kept as written.
:::
"""


def test_format_keeps_components_and_data_blocks(tmp_path: Path) -> None:
    (tmp_path / "page.md").write_text(MESSY, encoding="utf-8")
    (tmp_path / ".hidden").mkdir()
    (tmp_path / ".hidden" / "skip.md").write_text("* x\n", encoding="utf-8")
    assert format_docs(tmp_path, check=True) == [Path("page.md")]
    assert (tmp_path / "page.md").read_text(encoding="utf-8") == MESSY  # check changes nothing
    assert format_docs(tmp_path) == [Path("page.md")]
    text = (tmp_path / "page.md").read_text(encoding="utf-8")
    assert "- a\n- b\n" in text  # Markdown is formatted
    assert ":::steps\n1. One\n2. Two\n:::" in text  # the fence stays after the list
    assert "KEY=        # Aligned." in text  # env lines keep their columns
    assert "title: Page" in text
    assert format_docs(tmp_path) == []  # stable
    assert (tmp_path / ".hidden" / "skip.md").read_text(encoding="utf-8") == "* x\n"


def test_format_check_fails_on_unformatted_pages(make_site, capsys) -> None:
    root = make_site({"index.md": "# Home\n\n* a\n"})
    assert main(["format", "--check", "--root", str(root)]) == 1
    assert "not formatted: index.md" in capsys.readouterr().out
    assert main(["format", "--root", str(root)]) == 0
    assert main(["format", "--check", "--root", str(root)]) == 0
