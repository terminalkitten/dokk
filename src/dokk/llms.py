"""llms.txt (https://llmstxt.org): a Markdown index of the site for AI tools, plus llms-full.txt."""

from collections.abc import Callable

from dokk.config import Config
from dokk.content import Page
from dokk.menu import Nav, ordered_pages


def llms_txt(cfg: Config, nav: list[Nav], absolute: Callable[[Page], str]) -> str:
    """One section per top-level sidebar group, one link per page."""
    lines = [f"# {cfg.title}", ""]
    if cfg.description:
        lines += [f"> {cfg.description}", ""]
    loose: list[Nav] = []
    sections: list[tuple[str, list[Nav]]] = []
    for n in nav:
        if n.children is None:
            loose.append(n)
        else:
            sections.append((n.label or "Pages", n.children))
    if loose:
        sections.insert(0, ("Pages", loose))
    for label, items in sections:
        pages = [p for p in ordered_pages(items) if not p.noindex]
        if not pages:
            continue
        lines += [f"## {label}", ""]
        for p in pages:
            desc = f": {p.description}" if p.description else ""
            lines.append(f"- [{p.title}]({absolute(p)}){desc}")
        lines.append("")
    return "\n".join(lines)


def llms_full_txt(cfg: Config, pages: list[Page], absolute: Callable[[Page], str]) -> str:
    """Every page's Markdown source in one file, in menu order."""
    parts = [f"# {cfg.title}\n"]
    for p in pages:
        if not p.noindex:
            parts.append(f"\n---\n\n# {p.title}\n\nURL: {absolute(p)}\n\n{p.body.strip()}\n")
    return "".join(parts)
