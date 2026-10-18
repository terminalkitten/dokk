from pathlib import Path

import pytest

from dokk.config import ConfigError, base_path_from, load_config


@pytest.mark.parametrize(
    ("site_url", "expected"),
    [
        ("", ""),
        ("https://example.com", ""),
        ("https://example.com/", ""),
        ("https://example.github.io/repo/", "/repo"),
        ("https://example.com/a/b", "/a/b"),
    ],
)
def test_base_path_from(site_url: str, expected: str) -> None:
    assert base_path_from(site_url) == expected


def test_defaults(make_site) -> None:
    root = make_site({"index.md": "hi"})
    cfg = load_config(root)
    assert cfg.title == "Test"
    assert cfg.content_dir == root / "docs"
    assert cfg.out_dir == (root / "dist").resolve()
    assert cfg.base_path == ""


def test_dev_forces_empty_base_path(make_site) -> None:
    root = make_site({}, 'title = "T"\nsite_url = "https://x.io/repo/"\n')
    assert load_config(root).base_path == "/repo"
    assert load_config(root, dev=True).base_path == ""


@pytest.mark.parametrize(
    ("toml", "message"),
    [
        ('description = "x"\n', "'title' is required"),
        ("title = 3\n", "'title' must be a string"),
        ('title = "T"\nbogus = 1\n', "unknown key(s): bogus"),
        ('title = "T"\nsite_url = "example.com"\n', "site_url"),
        ('title = "T"\nout_dir = "."\n', "out_dir"),
        ('title = "T"\ncontent_dir = "."\n', "must not contain 'out_dir'"),
        ('title = "T"\nout_dir = "docs/out"\n', "must not contain 'out_dir'"),
        ('title = "T"\ntheme = "x"\n', "[theme] must be a table"),
        ("title = \n", "dokk.toml"),
        ('title = "T"\n[theme]\ncode_dark = "nope"\n', "unknown Pygments style 'nope'"),
        ('title = "T"\n[theme]\nfont = "x"\n', "unknown [theme] key(s): font"),
        (
            'title = "T"\n[theme]\nstyle = "comic"\n',
            "unknown theme.style 'comic'; choose from vega",
        ),
        ('title = "T"\n[theme]\ncolor = "zinc"\n', "unknown theme.color 'zinc'; choose from amber"),
        ('title = "T"\n[theme]\nbase = "pink"\n', "unknown theme.base 'pink'; choose from neutral"),
        (
            'title = "T"\n[llms]\nenable = true\n',
            "unknown [llms] key(s): enable (supported: enabled)",
        ),
        ('title = "T"\n[search]\nenabled = "no"\n', "'search.enabled' must be true or false"),
    ],
)
def test_errors(make_site, toml: str, message: str) -> None:
    root = make_site({}, toml)
    with pytest.raises(ConfigError, match=None) as exc:
        load_config(root)
    assert message in str(exc.value)


def test_missing_config(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="no dokk.toml"):
        load_config(tmp_path)


def test_theme_config(make_site) -> None:
    from pygments.styles import get_style_by_name

    from dokk.themes import ACCENTS, code_styles

    for color in ("", *ACCENTS):
        light, dark = code_styles(color)
        get_style_by_name(light), get_style_by_name(dark)  # all exist
    root = make_site({}, 'title = "T"\n[theme]\nstyle = "rhea"\ncolor = "pink"\n')
    assert load_config(root).theme == {
        "style": "rhea",
        "base": "neutral",
        "color": "pink",
        "code_light": "pastie",
        "code_dark": "monokai",
    }
    root = make_site({}, 'title = "T"\n[theme]\ncolor = "pink"\ncode_dark = "nord"\n')
    assert load_config(root).theme["code_dark"] == "nord"  # explicit wins
    defaults = load_config(make_site({}, 'title = "T"\n')).theme
    assert (defaults["style"], defaults["base"], defaults["color"]) == ("vega", "neutral", "")
