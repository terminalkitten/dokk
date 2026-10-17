from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any

from dokk.content import Page, titleize
from dokk.tree import Node


@dataclass(frozen=True)
class Crumb:
    label: str
    url: str | None


def badge_html(page: Page) -> str:
    badge = page.sidebar.get("badge")
    if not badge:
        return ""
    if isinstance(badge, dict):
        text, variant = badge.get("text", ""), badge.get("variant", "secondary")
    else:
        text, variant = badge, "secondary"
    return f' <span class="badge" data-variant="{escape(str(variant))}">{escape(str(text))}</span>'


def _item(page: Page, label: str, route: str) -> dict[str, Any]:
    # The Basecoat macro emits item labels with |safe, so escape here.
    return {
        "type": "item",
        "label": escape(label) + badge_html(page),
        "url": page.url,
        "current": page.route == route,
    }


def _index_label(page: Page) -> str:
    return str(page.sidebar.get("label") or "Overview")


def _folder_items(node: Node, route: str) -> list[dict[str, Any]]:
    items = [_item(node.page, _index_label(node.page), route)] if node.page else []
    for child in node.children:
        if child.is_dir:
            sub = _folder_items(child, route)
            items.append(
                {
                    "type": "submenu",
                    "label": escape(child.label),  # |safe in the macro too
                    "open": _contains_current(sub),
                    "items": sub,
                }
            )
        else:
            assert child.page
            items.append(_item(child.page, child.label, route))
    return items


def _contains_current(items: list[dict[str, Any]]) -> bool:
    return any(i.get("current") or _contains_current(i.get("items", [])) for i in items)


def build_menu(root: Node, route: str) -> list[dict[str, Any]]:
    """Basecoat sidebar menu for the page at `route`.

    Root pages form a first unlabeled group, each root folder its own group.
    """
    # ponytail: rebuilt per page, O(pages^2) overall; fine at ~1000 pages.
    loose = [_item(c.page, c.label, route) for c in root.children if not c.is_dir and c.page]
    if root.page:
        loose.insert(
            0, _item(root.page, str(root.page.sidebar.get("label") or root.page.title), route)
        )
    menu: list[dict[str, Any]] = [{"type": "group", "items": loose}] if loose else []
    for child in root.children:
        if child.is_dir:
            # Group labels are escaped by the macro itself: pass them raw.
            menu.append(
                {"type": "group", "label": child.label, "items": _folder_items(child, route)}
            )
    return menu


def ordered_pages(root: Node) -> list[Page]:
    """Pages in menu order, for prev/next links."""
    loose = [c.page for c in root.children if not c.is_dir and c.page]
    pages = ([root.page] if root.page else []) + loose

    def walk(node: Node) -> None:
        if node.page:
            pages.append(node.page)
        for child in node.children:
            if child.is_dir:
                walk(child)
            elif child.page:
                pages.append(child.page)

    for child in root.children:
        if child.is_dir:
            walk(child)
    return pages


def prev_next(order: list[Page], page: Page) -> tuple[Page | None, Page | None]:
    if page not in order:
        return None, None
    i = order.index(page)
    return (order[i - 1] if i > 0 else None), (order[i + 1] if i + 1 < len(order) else None)


def breadcrumbs(page: Page, index_pages: dict[Path, Page]) -> list[Crumb]:
    """Ancestor folders (linked if they have an index page), then the page itself.

    `index_pages` maps a folder (relative to content_dir) to its index page.
    """
    folders = list(page.rel.parents)[::-1][1:]  # skip the content root
    if page.rel.stem == "index":
        folders = folders[:-1]  # the folder is this page
    crumbs = []
    for folder in folders:
        index = index_pages.get(folder)
        if index:
            crumbs.append(Crumb(index.title, index.url))
        else:
            crumbs.append(Crumb(titleize(folder.name), None))
    return [*crumbs, Crumb(page.title, None)]
