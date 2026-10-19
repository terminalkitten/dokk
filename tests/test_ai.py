import re
from pathlib import Path

import pytest

from dokk.ai import bench_scores, env_lines, mark_variables
from dokk.directives import DirectiveError
from dokk.markdown import Renderer
from dokk.render import base_env


@pytest.fixture
def renderer(tmp_path: Path) -> Renderer:
    return Renderer({"index.md": "/"}, tmp_path, "", base_env())


def _render(renderer: Renderer, body: str) -> str:
    return renderer.render(body, Path("page.md")).html


def test_env_lines() -> None:
    rows = env_lines("API_KEY=   # Your key.\n# a comment\n\nMODEL=small  # The model.\nDEBUG=1\n")
    assert rows == [
        {"name": "API_KEY", "default": "", "description": "Your key."},
        {"name": "MODEL", "default": "small", "description": "The model."},
        {"name": "DEBUG", "default": "1", "description": ""},
    ]
    with pytest.raises(ValueError, match="NAME=value"):
        env_lines("export API_KEY\n")


def test_bench_scores() -> None:
    scores = bench_scores("- Big: 80%\nSmall: 40 %\n", "")
    assert [(s["label"], s["text"], s["width"]) for s in scores] == [
        ("Big", "80%", 100.0),  # relative to the best score
        ("Small", "40%", 50.0),
    ]
    assert bench_scores("A: 150\n", "100")[0]["width"] == 100.0  # capped
    with pytest.raises(ValueError, match="Label: 88.7"):
        bench_scores("just text\n", "")


def test_mark_variables() -> None:
    assert mark_variables("<p>Hi {{ name }} and {{x}}</p>") == (
        '<p>Hi <mark class="dk-prompt-var" data-var="name">{{ name }}</mark> and '
        '<mark class="dk-prompt-var" data-var="x">{{ x }}</mark></p>'
    )


def test_chat(renderer: Renderer) -> None:
    html = _render(
        renderer,
        "::::chat[Demo]\n:::system\nBe brief.\n:::\n:::user\nHi & bye\n:::\n"
        ':::assistant[Claude]{icon="claude"}\nHello **you**.\n:::\n::::\n',
    )
    assert '<figure class="dk-chat" id="dk-chat-1">' in html
    assert "<figcaption>Demo</figcaption>" in html
    assert '<div class="dk-msg" data-role="system">' in html
    assert '<div class="dk-msg-bubble"><p>Hi &amp; bye</p>' in html
    assert '<span class="dk-msg-avatar"><svg' in html and 'class="dk-vendor-logo"' in html
    assert "<p>Hello <strong>you</strong>.</p>" in html
    with pytest.raises(DirectiveError, match='unknown icon "acme"'):
        _render(renderer, ':::assistant{icon="acme"}\nHi\n:::\n')


TOOL = """:::tool
Call it *first*.

```json
{"type": "function", "function": {"name": "get_weather", "description": "Weather now.",
 "parameters": {"type": "object", "required": ["city"], "properties": {
   "city": {"type": "string", "description": "A <city>."},
   "days": {"type": "array", "items": {"type": "integer"}, "default": [1]},
   "unit": {"enum": ["c", "f"]},
   "note": {"anyOf": [{"type": "string"}, {"type": "null"}]}}}}}
```
:::
"""


def test_tool_from_an_openai_function(renderer: Renderer) -> None:
    html = _render(renderer, TOOL)
    assert "<code>get_weather</code>" in html
    assert "<p>Weather now.</p>" in html
    assert "<p>Call it <em>first</em>.</p>" in html  # the body, without the JSON block
    assert html.count('<pre class="code hl">') == 1  # the JSON shows once, in its <details>
    row = r"<tr>\s*<td><code>(\w+)</code>(.*?)</td>\s*<td><code>(.*?)</code>"
    rows = re.findall(row, html, re.S)
    assert [(n, "required" in r, t) for n, r, t in rows] == [
        ("city", True, "string"),
        ("days", False, "integer[]"),
        ("unit", False, "any"),
        ("note", False, "string | null"),
    ]
    assert "A &lt;city&gt;." in html
    assert "Default <code>[1]</code>" in html
    assert "One of <code>&#34;c&#34;</code>, <code>&#34;f&#34;</code>" in html


def test_tool_errors(renderer: Renderer) -> None:
    with pytest.raises(DirectiveError, match=r"line 1: a tool needs a ```json block"):
        _render(renderer, ":::tool[x]\nNo schema.\n:::\n")
    with pytest.raises(DirectiveError, match="the tool's JSON is invalid"):
        _render(renderer, ":::tool[x]\n```json\n{oops\n```\n:::\n")


def test_trace(renderer: Renderer) -> None:
    html = _render(
        renderer,
        '::::trace[Run]\n:::step[Searched]{icon="search"}\n:::\n'
        ':::step[Ran tests]{status="error"}\nFAILED\n:::\n::::\n',
    )
    assert '<p class="dk-trace-title">Run</p>' in html
    assert html.count('<li class="dk-step"') == 2
    assert '<div class="dk-step-line"><span class="dk-step-icon"><svg' in html  # no body: a line
    assert re.search(r'data-status="error">\s*<details><summary>', html)  # a body: it opens
    assert '<div class="dk-step-body"><p>FAILED</p>' in html
    with pytest.raises(DirectiveError, match="must be inside '::::trace'"):
        _render(renderer, ":::step[x]\n:::\n")
    with pytest.raises(DirectiveError, match='unknown icon "rocketship"'):
        _render(renderer, '::::trace\n:::step[x]{icon="rocketship"}\n:::\n::::\n')
    with pytest.raises(DirectiveError, match="status must be one of done, running, error"):
        _render(renderer, '::::trace\n:::step[x]{status="ok"}\n:::\n::::\n')


def test_models_table(renderer: Renderer) -> None:
    html = _render(
        renderer,
        '::::models\n::model[A]{icon="openai" input="3" features="tools"}\n'
        '::model[B]{context="32K"}\n::::\n',
    )
    assert '<span class="dk-models-name"><svg' in html
    input_row = r'<th scope="row">Input / 1M</th>\s*<td>\$3</td>\s*<td><span class="dk-models-n'
    assert re.search(input_row, html)
    assert '<th scope="row">Context</th>' in html
    assert "Output / 1M" not in html  # no model has it
    assert '<article class="card dk-model"' not in html  # the cards become the table
    with pytest.raises(DirectiveError, match="may only contain ':::model'"):
        _render(renderer, "::::models\n:::note\nx\n:::\n::::\n")


def test_bench(renderer: Renderer) -> None:
    html = _render(renderer, ':::bench[Eval]{highlight="Ours"}\nOurs: 90%\nTheirs: 45%\n:::\n')
    assert "<figcaption>Eval</figcaption>" in html
    assert "<div data-highlight>\n      <dt>Ours</dt>" in html
    assert 'style="width: 50.0%"' in html
    with pytest.raises(DirectiveError, match="line 1: write bench lines"):
        _render(renderer, ":::bench\nnothing\n:::\n")


def test_install(renderer: Renderer) -> None:
    html = _render(
        renderer, '::install[dokk[search]]\n\n::install[pytest]{dev="true" tools="uv"}\n'
    )
    assert 'data-sync="install"' in html
    assert '<span class="s2">"dokk[search]"</span>' in html  # quoted for the shell
    assert "--dev" in html
    assert "poetry" in html.split('id="dk-install-2"')[0]  # all three by default
    assert "poetry" not in html.split('id="dk-install-2"')[1]  # tools="uv"
    with pytest.raises(DirectiveError, match="unknown installer 'conda'"):
        _render(renderer, '::install[x]{tools="conda"}\n')
    with pytest.raises(DirectiveError, match=r"use ::install\[package\]"):
        _render(renderer, "::install\n")


def test_env(renderer: Renderer) -> None:
    html = _render(renderer, ":::env\nAPI_KEY=  # Your <key>.\nMODEL=small\n:::\n")
    assert '<td><code>API_KEY</code> <span class="badge" data-variant="secondary">required' in html
    assert "<td><code>small</code></td>" in html
    assert "Your &lt;key&gt;." in html
    assert 'data-dk-copy-text="API_KEY=  # Your &lt;key&gt;.\nMODEL=small"' in html


def test_prompt_variables(renderer: Renderer) -> None:
    html = _render(renderer, ":::prompt\nFix {{ error }} in {{lang}}, then {{ error }}.\n:::\n")
    assert html.count('data-dk-prompt-var="') == 2  # each variable once
    assert '<mark class="dk-prompt-var" data-var="error">{{ error }}</mark>' in html
