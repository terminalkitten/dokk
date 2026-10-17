from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markupsafe import Markup

from dokk.assets import ASSETS_DIR
from dokk.config import Config
from dokk.routes import url_for

BUILTIN_TEMPLATES = Path(__file__).parent / "templates"


def base_env(user_templates: Path | None = None) -> Environment:
    search_path = [p for p in (user_templates, BUILTIN_TEMPLATES) if p and p.is_dir()]
    return Environment(
        loader=FileSystemLoader(search_path),  # user overrides win
        autoescape=select_autoescape(["html", "jinja"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def make_env(cfg: Config) -> Environment:
    env = base_env(cfg.root / "templates")

    def url(route: str) -> str:
        return url_for(cfg.base_path, route)

    def asset(path: str) -> str:
        return url(f"/{ASSETS_DIR}/{path}")

    env.globals.update(
        url=url,
        asset=asset,
        site={
            "title": cfg.title,
            "description": cfg.description,
            "lang": cfg.lang,
            "site_url": cfg.site_url,
            "links": cfg.links,
        },
        # The sidebar macro emits `header` with |safe, so build it as escaped Markup.
        sidebar_header=Markup('<a class="dk-brand" href="{}">{}</a>').format(url("/"), cfg.title),
    )
    return env


def canonical(cfg: Config, route: str) -> str:
    return cfg.site_url.rstrip("/") + route if cfg.site_url else ""


def render_template(env: Environment, name: str, **ctx: Any) -> str:
    return env.get_template(name).render(**ctx)
