from pathlib import Path

from dokk.assets import copy_page_assets


def test_copy_page_assets(tmp_path: Path) -> None:
    content, out = tmp_path / "docs", tmp_path / "out"
    for rel in ("a.md", "img/x.png", "sub/deep/y.svg", ".DS_Store", ".hidden/z.png"):
        (content / rel).parent.mkdir(parents=True, exist_ok=True)
        (content / rel).write_text(rel, encoding="utf-8")
    copy_page_assets(content, out)
    files = sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())
    assert files == ["img/x.png", "sub/deep/y.svg"]
