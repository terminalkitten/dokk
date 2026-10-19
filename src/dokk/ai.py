"""Data for the AI and Python components, worked out from what the author wrote: a tool's
JSON schema, `.env` lines, benchmark scores, install commands and prompt variables.
Templates in components/ only lay it out.
"""

import json
import re
import shlex
from collections.abc import Callable
from typing import Any

from markdown_it.token import Token
from markupsafe import Markup

from dokk.directives import Directive, DirectiveError

INSTALLERS = ("pip", "uv", "poetry")
_VARIABLE = re.compile(r"\{\{\s*([A-Za-z_][\w-]*)\s*\}\}")
_ENV = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*?)(?:\s+#\s?(.*))?$")
_SCORE = re.compile(r"^(.+?):\s*(-?\d+(?:\.\d+)?)\s*(\S*)$")


def component_data(
    d: Directive, inner: list[Token], source: str, highlight: Callable[[str, str], str]
) -> dict[str, Any]:
    """Extra template values for directive `d`; `source` is its Markdown as written."""
    try:
        if d.name == "tool":
            return tool_schema(inner, highlight)
        if d.name == "env":
            return {"variables": env_lines(source), "source": source}
        if d.name == "bench":
            return {"scores": bench_scores(source, d.attrs.get("max", ""))}
        if d.name == "install":
            return {"commands": install_commands(d, highlight)}
        if d.name == "prompt":
            return {"source": source, "variables": list(dict.fromkeys(_VARIABLE.findall(source)))}
    except ValueError as e:
        raise DirectiveError(f"line {d.line}: {e}") from None
    return {}


def mark_variables(html: str) -> str:
    """{{ name }} in a rendered prompt, wrapped so the page can fill it in."""
    return _VARIABLE.sub(r'<mark class="dk-prompt-var" data-var="\1">{{ \1 }}</mark>', html)


def tool_schema(inner: list[Token], highlight: Callable[[str, str], str]) -> dict[str, Any]:
    """A tool definition from the first ```json block: an OpenAI or Anthropic tool, or a bare
    JSON schema. The block itself is kept, collapsed, under the parameter table."""
    fence = next((t for t in inner if t.type == "fence" and t.info.split()[:1] == ["json"]), None)
    if fence is None:
        raise ValueError("a tool needs a ```json block with its schema")
    try:
        data = json.loads(fence.content)
    except json.JSONDecodeError as e:
        raise ValueError(f"the tool's JSON is invalid: {e}") from None
    tool = data.get("function", data) if isinstance(data, dict) else {}
    schema = tool.get("parameters") or tool.get("input_schema") or tool
    if not isinstance(schema, dict) or not isinstance(schema.get("properties", {}), dict):
        raise ValueError("the tool's JSON has no object schema with properties")
    required = set(schema.get("required", []))
    params = [
        {
            "name": name,
            "type": _type_name(spec),
            "required": name in required,
            "description": spec.get("description", ""),
            "default": json.dumps(spec["default"]) if "default" in spec else "",
            "enum": [json.dumps(v) for v in spec.get("enum", [])],
        }
        for name, spec in schema.get("properties", {}).items()
        if isinstance(spec, dict)
    ]
    return {
        "tool_name": tool.get("name", ""),
        "tool_description": tool.get("description", ""),
        "params": params,
        "schema_html": Markup(highlight(fence.content, "json")),
        "fence": fence,
    }


def _type_name(spec: dict[str, Any]) -> str:
    kind = spec.get("type", "")
    if isinstance(kind, list):
        return " | ".join(str(k) for k in kind)
    if kind == "array" and isinstance(spec.get("items"), dict):
        return f"{_type_name(spec['items']) or 'any'}[]"
    if not kind and ("anyOf" in spec or "oneOf" in spec):
        return " | ".join(_type_name(s) for s in spec.get("anyOf", spec.get("oneOf", [])))
    return str(kind)


def env_lines(source: str) -> list[dict[str, str]]:
    """`NAME=default  # description` lines, as in a .env file; an empty value is required."""
    rows = []
    for line in source.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = _ENV.match(line)
        if not match:
            raise ValueError(f"write env lines as NAME=value  # description, not {line!r}")
        name, value, description = match.groups()
        rows.append({"name": name, "default": value.strip(), "description": description or ""})
    return rows


def bench_scores(source: str, maximum: str) -> list[dict[str, Any]]:
    """`Label: 88.7 %` lines; bars are relative to `maximum`, else to the best score."""
    rows: list[tuple[str, float, str]] = []
    for line in source.splitlines():
        line = line.strip().removeprefix("- ")
        if not line:
            continue
        match = _SCORE.match(line)
        if not match:
            raise ValueError(f"write bench lines as 'Label: 88.7', not {line!r}")
        label, number, unit = match.groups()
        rows.append((label.strip(), float(number), number + unit))
    top = float(maximum) if maximum else max((v for _, v, _ in rows), default=0.0) or 1.0
    scores = []
    for label, value, text in rows:
        width = round(min(100.0, max(0.0, value / top * 100)), 1)
        scores.append({"label": label, "value": value, "text": text, "width": width})
    return scores


def install_commands(d: Directive, highlight: Callable[[str, str], str]) -> list[dict[str, str]]:
    """pip, uv and poetry commands for `::install[package]`; dev="true" adds it for development."""
    if not d.title:
        raise ValueError("use ::install[package], such as ::install[dokk[search]]")
    package = shlex.quote(d.title) if "[" not in d.title else f'"{d.title}"'
    dev = d.attrs.get("dev") == "true"
    commands = {
        "pip": f"pip install {package}",
        "uv": f"uv add {'--dev ' if dev else ''}{package}",
        "poetry": f"poetry add {'--group dev ' if dev else ''}{package}",
    }
    names = d.attrs.get("tools", " ".join(INSTALLERS)).split()
    if unknown := [n for n in names if n not in commands]:
        raise ValueError(f"unknown installer {unknown[0]!r}; choose from {', '.join(INSTALLERS)}")
    return [{"name": n, "html": Markup(highlight(commands[n], "bash"))} for n in names]
