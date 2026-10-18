from pathlib import Path
from typing import Any
from urllib.parse import quote

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
        # Escape HTML and XML output; text formats (.txt, .md, .toml, .yml) stay as written.
        autoescape=select_autoescape(["html.jinja", "xml.jinja"], default=False),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


# Picked up from public/ when present, first match wins.
FAVICONS = ("favicon.svg", "favicon.ico", "favicon.png")
LOGOS = ("logo.svg", "logo.png")
# Where the footer's "Built with dokk" credit links to.
HOMEPAGE = "https://terminalkitten.github.io/dokk/"
DARK_LOGOS = ("logo-dark.svg", "logo-dark.png")


def make_env(cfg: Config, dev: bool = False, search: bool = False) -> Environment:
    env = base_env(cfg.root / "templates")

    def url(route: str) -> str:
        return url_for(cfg.base_path, route)

    def asset(path: str) -> str:
        return url(f"/{ASSETS_DIR}/{path}")

    def public(names: tuple[str, ...]) -> str:
        return next((url(f"/{n}") for n in names if (cfg.root / "public" / n).is_file()), "")

    template_globals: dict[str, Any] = dict(
        url=url,
        asset=asset,
        dev=dev,
        search=search,
        site={
            "title": cfg.title,
            "description": cfg.description,
            "lang": cfg.lang,
            "site_url": cfg.site_url,
            "links": cfg.links,
            "style": cfg.theme.get("style", "vega"),
            "favicon": public(FAVICONS),
            "logo": public(LOGOS),
            "logo_dark": public(DARK_LOGOS),
            "footer": cfg.footer or {"text": "", "credit": True},
            "homepage": HOMEPAGE,
        },
    )
    env.globals.update(template_globals)
    # The sidebar macro emits `header` with |safe; the template escapes the title.
    brand = Markup(render_template(env, "partials/brand.html.jinja"))
    header: dict[str, Any] = {
        "sidebar_header": Markup('<a class="dk-brand" href="{}">{}</a>').format(url("/"), brand)
    }
    env.globals.update(header)
    return env


def canonical(cfg: Config, route: str) -> str:
    return cfg.site_url.rstrip("/") + quote(route) if cfg.site_url else ""


def render_template(env: Environment, name: str, **ctx: Any) -> str:
    return env.get_template(name).render(**ctx)
