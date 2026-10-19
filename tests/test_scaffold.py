import subprocess
import sys
from pathlib import Path

import pytest

from dokk.cli import main
from dokk.themes import STYLES

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "src" / "dokk"


def test_help_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert "build" in capsys.readouterr().out


def test_python_m_dokk_runs() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "dokk", "--help"], capture_output=True, encoding="utf-8"
    )
    assert result.returncode == 0


@pytest.mark.parametrize(
    "rel",
    [
        *(f"static/vendor/basecoat/basecoat-{s}.cdn.min.css" for s in STYLES),
        "data/shadcn-themes.json",
        "data/SHADCN-LICENSE",
        "static/vendor/basecoat/all.min.js",
        "static/vendor/basecoat/LICENSE",
        "templates/basecoat/sidebar.html.jinja",
        "templates/basecoat/tabs.html.jinja",
    ],
)
def test_vendored_file_exists(rel: str) -> None:
    assert (PKG / rel).is_file()


def test_vendored_version_recorded() -> None:
    assert "basecoat-css@1.0.2" in (ROOT / "VENDORED.md").read_text(encoding="utf-8")
