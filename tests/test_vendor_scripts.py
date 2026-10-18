import base64
import hashlib
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def _load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_themes_from_ts() -> None:
    themes = _load("vendor_shadcn_themes").themes_from_ts(
        "export const THEMES = [\n"
        "  {\n"
        '    name: "neutral",\n'
        "    cssVars: {\n"  # one key per line, as in themes.ts
        "      light: {\n"
        '        background: "oklch(1 0 0)",\n'
        '        "chart-1": "x",\n'
        "      },\n"
        "      dark: {\n"
        '        background: "oklch(0.1 0 0)",\n'
        "      },\n"
        "    },\n"
        "  },\n"
        "] as const\n"
    )
    assert themes == {
        "neutral": {
            "light": {"background": "oklch(1 0 0)", "chart-1": "x"},
            "dark": {"background": "oklch(0.1 0 0)"},
        }
    }


def test_basecoat_integrity_and_destinations() -> None:
    vendor = _load("vendor_basecoat")
    data = b"tarball"
    good = "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode()
    vendor.check_integrity(data, good)
    with pytest.raises(SystemExit, match="integrity mismatch"):
        vendor.check_integrity(b"tampered", good)

    targets = vendor.destinations(
        ["package/templates/jinja/sidebar.html.jinja", "package/templates/nunjucks/x.njk"]
    )
    assert targets["package/LICENSE.md"] == vendor.STATIC / "LICENSE"
    assert targets["package/templates/jinja/sidebar.html.jinja"].name == "sidebar.html.jinja"
    assert "package/templates/nunjucks/x.njk" not in targets
    assert len(targets) == 8 + 1 + 1 + 1  # style packs, all.min.js, LICENSE, one macro
