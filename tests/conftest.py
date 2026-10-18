from collections.abc import Callable
from pathlib import Path

import pytest

SiteFactory = Callable[..., Path]


@pytest.fixture
def make_site(tmp_path: Path) -> SiteFactory:
    """Write a site: `files` maps paths under docs/ to their text."""

    def make(files: dict[str, str], toml: str = 'title = "Test"\n') -> Path:
        if "[search]" not in toml:
            toml += "\n[search]\nenabled = false\n"  # keep tests fast and pagefind-free
        (tmp_path / "docs").mkdir(exist_ok=True)
        (tmp_path / "dokk.toml").write_text(toml, encoding="utf-8")
        for rel, text in files.items():
            path = tmp_path / "docs" / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return tmp_path

    return make
