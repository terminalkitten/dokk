"""Navigation: sidebar tree (automatic or from dokk.toml), menu, breadcrumbs, prev/next."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from markupsafe import Markup, escape

from dokk import DokkError
from dokk.content import Page, titleize
from dokk.directives import DirectiveError
from dokk.directives import badge as badge_span
from dokk.tree import Node


class NavError(DokkError):
    pass


@dataclass(eq=False)
class Nav:
    """One sidebar entry: a page, an external link, or a labelled list of entries."""

    label: str
    page: Page | None = None
    link: str = ""
    children: list["Nav"] | None = None  # None for a leaf


@dataclass(frozen=True)
class Crumb:
    label: str
    url: str | None


def _page_label(page: Page) -> str:
    return str(page.sidebar.get("label") or page.title)


def _folder_nav(node: Node) -> list[Nav]:
    """A folder's index page (as "Overview" unless sidebar.label), then its children."""
    items = []
    if node.page:
        items.append(Nav(str(node.page.sidebar.get("label") or "Overview"), page=node.page))
    for child in node.children:
        if child.is_dir:
            items.append(Nav(child.label, children=_folder_nav(child)))
        elif child.page:
            items.append(Nav(child.label, page=child.page))
    return items


def auto_nav(root: Node) -> list[Nav]:
    """Root pages form a first unlabeled group, each root folder its own group."""
    loose = [Nav(_page_label(root.page), page=root.page)] if root.page else []
    loose += [Nav(c.label, page=c.page) for c in root.children if not c.is_dir and c.page]
    groups = [Nav("", children=loose)] if loose else []
    return groups + [Nav(c.label, children=_folder_nav(c)) for c in root.children if c.is_dir]


def config_nav(
    entries: list[Any], root: Node, pages: dict[str, Page], content_dir: Path, base_path: str
) -> list[Nav]:
    """The `[[sidebar]]` list from dokk.toml. Entries:

    "path.md"                          a page (label: sidebar.label or title)
    {page = "path.md", label = "..."}  a page with a custom label
    {label = "...", link = "https://..."}  an external (or root-absolute) link
    {label = "...", autogenerate = "folder"}  a folder, generated as without config
    {label = "...", items = [...]}     a group (top level) or submenu (nested)
    """

    def folder(path: str) -> Node:
        node = root
        for part in Path(path).parts:
            node = next((c for c in node.children if c.is_dir and c.name == part), None)  # type: ignore[assignment]
            if node is None:
                raise NavError(f"dokk.toml: sidebar: folder {path!r} not found")
        return node

    def entry(e: Any) -> Nav | None:
        if isinstance(e, str):
            e = {"page": e}
        if not isinstance(e, dict):
            raise NavError(f"dokk.toml: sidebar: unexpected entry {e!r}")
        label = str(e.get("label", ""))
        if "page" in e:
            page = pages.get(str(e["page"]))
            if page is None:
                if (content_dir / str(e["page"])).is_file():
                    return None  # a draft, left out of this build
                raise NavError(f"dokk.toml: sidebar: page {e['page']!r} not found")
            return Nav(label or _page_label(page), page=page)
        if "link" in e:
            if not label:
                raise NavError(f"dokk.toml: sidebar: link {e['link']!r} needs a label")
            link = str(e["link"])
            return Nav(label, link=base_path + link if link.startswith("/") else link)
        if "autogenerate" in e:
            node = folder(str(e["autogenerate"]))
            return Nav(label or node.label, children=_folder_nav(node))
        if "items" in e:
            return Nav(label, children=[n for n in map(entry, e["items"]) if n])
        raise NavError(f"dokk.toml: sidebar: entry needs page, link, autogenerate or items: {e!r}")

    return [n for n in map(entry, entries) if n]


def ordered_pages(nav: list[Nav]) -> list[Page]:
    """Pages in menu order (first occurrence), for prev/next links."""
    seen: dict[int, Page] = {}

    def walk(items: list[Nav]) -> None:
        for n in items:
            if n.page and id(n.page) not in seen:
                seen[id(n.page)] = n.page
            walk(n.children or [])

    walk(nav)
    return list(seen.values())


def submenu_keys(nav: list[Nav]) -> tuple[dict[int, str], dict[int, tuple[str, ...]]]:
    """Stable marker per submenu, and id(page) -> markers of the submenus around it."""
    keys: dict[int, str] = {}
    around: dict[int, tuple[str, ...]] = {}

    def walk(items: list[Nav], parents: tuple[str, ...], top: bool) -> None:
        for n in items:
            if n.page:
                around.setdefault(id(n.page), parents)
            if n.children is not None:
                if not top:  # top-level lists are groups, not submenus
                    keys[id(n)] = str(len(keys) + 1)
                walk(n.children, parents if top else (*parents, keys[id(n)]), False)

    walk(nav, (), True)
    return keys, around


def badge_html(page: Page) -> Markup:
    badge = page.sidebar.get("badge")
    if not badge:
        return Markup("")
    if isinstance(badge, dict):
        text, variant = badge.get("text", ""), badge.get("variant", "secondary")
    else:
        text, variant = badge, "secondary"
    try:
        return Markup(" ") + badge_span(str(text), str(variant))
    except DirectiveError as e:
        raise NavError(f"{page.rel.as_posix()}: sidebar.{e}") from None


def _menu_items(items: list[Nav], keys: dict[int, str]) -> list[dict[str, Any]]:
    # The Basecoat macro emits item and submenu labels with |safe, so escape here.
    out: list[dict[str, Any]] = []
    for n in items:
        if n.children is not None:
            out.append(
                {
                    "type": "submenu",
                    "label": escape(n.label),
                    "attrs": {"data-sub": keys.get(id(n), "")},
                    "items": _menu_items(n.children, keys),
                }
            )
        elif n.page:
            label = escape(n.label) + badge_html(n.page)
            out.append({"type": "item", "label": label, "url": n.page.url})
        else:
            out.append({"type": "item", "label": escape(n.label), "url": n.link})
    return out


def build_menu(nav: list[Nav], keys: dict[int, str] | None = None) -> list[dict[str, Any]]:
    """Basecoat sidebar menu. Top-level lists are groups; loose top-level leaves share one.

    Submenus get a `data-sub` marker from `keys`; `mark_current` opens them per page.
    """
    keys = keys if keys is not None else submenu_keys(nav)[0]
    menu: list[dict[str, Any]] = []
    for n in nav:
        if n.children is not None:
            # Group labels are escaped by the macro itself: pass them raw.
            menu.append({"type": "group", "label": n.label, "items": _menu_items(n.children, keys)})
        elif menu and menu[-1].get("loose"):
            menu[-1]["items"] += _menu_items([n], keys)
        else:
            menu.append({"type": "group", "loose": True, "items": _menu_items([n], keys)})
    return menu


def mark_current(sidebar_html: str, url: str, open_keys: tuple[str, ...] = ()) -> str:
    """Mark the current page and open its submenus in a once-rendered sidebar.

    Far cheaper than rendering the whole menu again for every page.
    Expects whitespace-collapsed HTML, so menu links read exactly `<a href="...`.
    """
    for key in open_keys:
        sidebar_html = sidebar_html.replace(f'data-sub="{key}"', f'open data-sub="{key}"', 1)
    link = Markup('<a href="{}"').format(url)
    return sidebar_html.replace(link, link + Markup(' aria-current="page"'), 1)


class Pager:
    """prev/next for many pages without rescanning the order each time."""

    def __init__(self, order: list[Page]) -> None:
        self.order = order
        self.index = {id(p): i for i, p in enumerate(order)}

    def __call__(self, page: Page) -> tuple[Page | None, Page | None]:
        i = self.index.get(id(page))
        if i is None:
            return None, None
        o = self.order
        return (o[i - 1] if i > 0 else None), (o[i + 1] if i + 1 < len(o) else None)


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
