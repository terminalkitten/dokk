from pathlib import Path

import pytest

from dokk.headings import strip_attrs
from dokk.markdown import Renderer
from dokk.render import base_env


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("History { #history }", "History"),
        ("Plain {#plain .big}", "Plain"),
        ('Keyed {: data-x="1 2" }', "Keyed"),
        ("Not attributes {here}", "Not attributes {here}"),
        ("Set {a, b}", "Set {a, b}"),
    ],
)
def test_strip_attrs(text: str, expected: str) -> None:
    assert strip_attrs(text) == expected


def test_heading_attributes(tmp_path: Path) -> None:
    body = (
        "## Alternatives { #alternatives }\n\n"
        '## Plain {#plain .big data-x="1 2"}\n\n'
        "### Code `x` { #code-x }\n\n"
        "## Braces {here}\n"
    )
    result = Renderer({}, tmp_path, "", base_env()).render(body, Path("p.md"))
    assert '<h2 id="alternatives">Alternatives <a class="header-anchor" href="#alternatives">' in (
        result.html
    )
    assert '<h2 data-x="1 2" class="big" id="plain">Plain <a' in result.html
    assert '<h3 id="code-x">Code <code>x</code> <a' in result.html
    assert '<h2 id="braces-here">Braces {here} <a' in result.html  # not an attribute block
    assert [(t.id, t.text) for t in result.toc] == [
        ("alternatives", "Alternatives"),
        ("plain", "Plain"),
        ("code-x", "Code x"),
        ("braces-here", "Braces {here}"),
    ]
