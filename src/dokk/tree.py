import math
import re
from dataclasses import dataclass, field

from dokk.content import Page, titleize


@dataclass
class Node:
    name: str  # directory name or file stem
    is_dir: bool
    page: Page | None = None  # file: the page; dir: its index page, if any
    children: list["Node"] = field(default_factory=list)

    @property
    def order(self) -> float:
        return float(self.page.sidebar.get("order", math.inf)) if self.page else math.inf

    @property
    def hidden(self) -> bool:
        return bool(self.page and self.page.sidebar.get("hidden"))

    @property
    def label(self) -> str:
        """Menu label. A folder uses its index title, a page its sidebar.label or title."""
        if self.is_dir:
            return self.page.title if self.page else titleize(self.name)
        assert self.page
        return str(self.page.sidebar.get("label") or self.page.title)


def natural_key(name: str) -> list[int | str]:
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def _sort_key(node: Node) -> tuple[float, list[int | str]]:
    return node.order, natural_key(node.name)


def _prune_and_sort(node: Node) -> bool:
    """Drop hidden and empty entries, sort the rest. Returns False if node should go."""
    if node.hidden:
        return False
    if node.is_dir:
        node.children = [c for c in node.children if _prune_and_sort(c)]
        node.children.sort(key=_sort_key)
        return node.page is not None or bool(node.children)
    return True


def build_tree(pages: list[Page]) -> Node:
    """Menu tree: folders and pages, sorted, without hidden entries."""
    root = Node(name="", is_dir=True)
    for page in pages:
        node = root
        for part in page.rel.parent.parts:
            child = next((c for c in node.children if c.is_dir and c.name == part), None)
            if child is None:
                child = Node(name=part, is_dir=True)
                node.children.append(child)
            node = child
        if page.rel.stem == "index":
            node.page = page
        else:
            node.children.append(Node(name=page.rel.stem, is_dir=False, page=page))
    if root.hidden:
        root.page = None  # a hidden home page hides itself, not the whole site
    _prune_and_sort(root)
    return root
