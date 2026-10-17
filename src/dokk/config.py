import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pygments.styles import get_style_by_name
from pygments.util import ClassNotFound

from dokk import DokkError

CONFIG_FILE = "dokk.toml"
_KNOWN_KEYS = {
    "title",
    "description",
    "site_url",
    "content_dir",
    "out_dir",
    "lang",
    "theme",
    "links",
    "search",
}


class ConfigError(DokkError):
    pass


@dataclass(frozen=True)
class Config:
    root: Path
    title: str
    description: str = ""
    site_url: str = ""
    content_dir: Path = Path("docs")
    out_dir: Path = Path("dist")
    lang: str = "en"
    base_path: str = ""
    theme: dict[str, Any] = field(default_factory=dict)
    links: dict[str, Any] = field(default_factory=dict)
    search: dict[str, Any] = field(default_factory=dict)


def _str(data: dict[str, Any], key: str, default: str) -> str:
    value = data.get(key, default)
    if not isinstance(value, str):
        raise ConfigError(f"{CONFIG_FILE}: '{key}' must be a string")
    return value


def _table(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key, {})
    if not isinstance(value, dict):
        raise ConfigError(f"{CONFIG_FILE}: [{key}] must be a table")
    return value


def base_path_from(site_url: str) -> str:
    return urlparse(site_url).path.rstrip("/")


def load_config(root: Path, dev: bool = False) -> Config:
    root = root.resolve()
    path = root / CONFIG_FILE
    if not path.is_file():
        raise ConfigError(f"no {CONFIG_FILE} found in {root}")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"{CONFIG_FILE}: {e}") from e

    unknown = sorted(set(data) - _KNOWN_KEYS)
    if unknown:
        raise ConfigError(f"{CONFIG_FILE}: unknown key(s): {', '.join(unknown)}")
    title = _str(data, "title", "")
    if not title:
        raise ConfigError(f"{CONFIG_FILE}: 'title' is required")

    site_url = _str(data, "site_url", "")
    if site_url and urlparse(site_url).scheme not in ("http", "https"):
        raise ConfigError(f"{CONFIG_FILE}: 'site_url' must start with http:// or https://")

    content_dir = root / _str(data, "content_dir", "docs")
    if not content_dir.is_dir():
        raise ConfigError(f"content directory not found: {content_dir}")
    out_dir = (root / _str(data, "out_dir", "dist")).resolve()
    content = content_dir.resolve()
    if out_dir == root or out_dir in root.parents or content.is_relative_to(out_dir):
        raise ConfigError(f"{CONFIG_FILE}: 'out_dir' must not contain the site or its content")
    if out_dir.is_relative_to(content) or (root / ".dokk").is_relative_to(content):
        raise ConfigError(f"{CONFIG_FILE}: 'content_dir' must not contain 'out_dir' or .dokk/")

    theme = {"code_light": "default", "code_dark": "github-dark", **_table(data, "theme")}
    for key in ("code_light", "code_dark"):
        try:
            get_style_by_name(theme[key])
        except ClassNotFound:
            raise ConfigError(
                f"{CONFIG_FILE}: unknown Pygments style {theme[key]!r} for theme.{key}"
            ) from None

    return Config(
        root=root,
        title=title,
        description=_str(data, "description", ""),
        site_url=site_url,
        content_dir=content_dir,
        out_dir=out_dir,
        lang=_str(data, "lang", "en"),
        base_path="" if dev else base_path_from(site_url),
        theme=theme,
        links=_table(data, "links"),
        search=_table(data, "search"),
    )
