"""Maintainers only: vendor shadcn/ui's color themes (MIT) as JSON. Python stdlib only, no Node.

Usage: python scripts/vendor_shadcn_themes.py [commit]

Reads apps/v4/registry/themes.ts at a pinned commit and writes src/dokk/data/shadcn-themes.json.
The TypeScript is converted as text and parsed as JSON, never executed. Overwrites in place;
update VENDORED.md with the printed commit.
"""

import json
import re
import sys
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src/dokk/data"
COMMIT = "d2fba50ee5b9113008b5bb908563527b7efd2f27"

_BARE_KEY = re.compile(r"^(\s*)([A-Za-z_][\w-]*):", re.MULTILINE)
_TRAILING_COMMA = re.compile(r",(\s*[}\]])")


def fetch(url: str) -> str:
    with urlopen(url, timeout=60) as response:
        return response.read().decode("utf-8")


def themes_from_ts(source: str) -> dict[str, dict[str, dict[str, str]]]:
    """The THEMES array of themes.ts as {name: {"light": vars, "dark": vars}}."""
    body = source[source.index("= [") + 2 : source.index("\n] as const") + 2]
    body = _TRAILING_COMMA.sub(r"\1", _BARE_KEY.sub(r'\1"\2":', body))
    return {
        t["name"]: {"light": t["cssVars"]["light"], "dark": t["cssVars"]["dark"]}
        for t in json.loads(body)
    }


def main(commit: str = COMMIT) -> None:
    raw = f"https://raw.githubusercontent.com/shadcn-ui/ui/{commit}"
    themes = themes_from_ts(fetch(f"{raw}/apps/v4/registry/themes.ts"))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "SHADCN-LICENSE").write_text(fetch(f"{raw}/LICENSE.md"), encoding="utf-8")
    # indent=1 and raw UTF-8: the same bytes the earlier Node script wrote.
    text = json.dumps(themes, indent=1, ensure_ascii=False) + "\n"
    (OUT / "shadcn-themes.json").write_text(text, encoding="utf-8")
    print(f"Vendored {len(themes)} shadcn themes from commit {commit}")


if __name__ == "__main__":
    main(*sys.argv[1:2])
