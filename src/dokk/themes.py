import json
from pathlib import Path

STYLES = ("vega", "nova", "maia", "lyra", "mira", "luma", "sera", "rhea")

_THEMES: dict[str, dict[str, dict[str, str]]] = json.loads(
    (Path(__file__).parent / "data" / "shadcn-themes.json").read_text(encoding="utf-8")
)
BASES = tuple(name for name, t in _THEMES.items() if "background" in t["light"])
ACCENTS = tuple(name for name in _THEMES if name not in BASES)

# Code highlighting that suits each accent; without an accent: default / github-dark.
_CODE_STYLES = {
    "amber": ("gruvbox-light", "gruvbox-dark"),
    "blue": ("vs", "one-dark"),
    "cyan": ("solarized-light", "solarized-dark"),
    "emerald": ("friendly", "nord"),
    "fuchsia": ("lovelace", "dracula"),
    "green": ("friendly", "nord"),
    "indigo": ("vs", "one-dark"),
    "lime": ("friendly", "nord"),
    "orange": ("gruvbox-light", "gruvbox-dark"),
    "pink": ("pastie", "monokai"),
    "purple": ("lovelace", "dracula"),
    "red": ("pastie", "monokai"),
    "rose": ("pastie", "monokai"),
    "sky": ("vs", "one-dark"),
    "teal": ("solarized-light", "solarized-dark"),
    "violet": ("lovelace", "dracula"),
    "yellow": ("gruvbox-light", "gruvbox-dark"),
}


def code_styles(color: str) -> tuple[str, str]:
    return _CODE_STYLES.get(color, ("default", "github-dark"))


def theme_vars(base: str, color: str) -> dict[str, dict[str, str]]:
    """{"light": {...}, "dark": {...}}: the base theme with the accent on top.

    `radius` is left to the style pack, which owns shape.
    """
    accent = _THEMES[color] if color else {"light": {}, "dark": {}}
    return {
        mode: {k: v for k, v in {**_THEMES[base][mode], **accent[mode]}.items() if k != "radius"}
        for mode in ("light", "dark")
    }
