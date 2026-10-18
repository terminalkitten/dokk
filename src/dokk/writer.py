from pathlib import Path
from typing import Any

from jinja2 import Environment


class SiteWriter:
    """Writes every generated file. Templated output goes through render(), so the
    one way to produce a file is: prepare data in Python, lay it out in templates/."""

    def __init__(self, env: Environment, root: Path) -> None:
        self.env = env
        self.root = root

    def render(self, rel: Path | str, template: str, **ctx: Any) -> None:
        self.text(rel, self.env.get_template(template).render(**ctx))

    def text(self, rel: Path | str, content: str) -> None:
        """For content that is not templated, like generated CSS or an empty marker file."""
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
