"""Data for llms.txt and llms-full.txt; the layout lives in templates/files/."""

from dokk.content import Page
from dokk.menu import Nav, ordered_pages


def llms_sections(nav: list[Nav]) -> list[tuple[str, list[Page]]]:
    """One section per top-level sidebar group; loose top-level pages come first."""
    loose = [n for n in nav if n.children is None]
    sections = [("Pages", loose)] if loose else []
    sections += [(n.label or "Pages", n.children) for n in nav if n.children is not None]
    result = []
    for label, items in sections:
        pages = [p for p in ordered_pages(items) if not p.noindex]
        if pages:
            result.append((label, pages))
    return result
