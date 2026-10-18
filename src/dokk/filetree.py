"""File trees from a Markdown list, like Starlight's <FileTree>.

- a nested list, or a trailing "/", makes a directory
- **name** highlights an entry; text after the name is a comment
- ... or … is a placeholder; `backticks` escape names with spaces or underscores
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from markdown_it.token import Token
from markupsafe import Markup

from dokk import DokkError

PLACEHOLDERS = ("...", "…")


@dataclass
class Entry:
    name: str
    comment: Markup = Markup("")
    highlight: bool = False
    children: list["Entry"] = field(default_factory=list)

    @property
    def is_dir(self) -> bool:
        return bool(self.children) or self.name.endswith("/")

    @property
    def placeholder(self) -> bool:
        return self.name in PLACEHOLDERS


def _split(children: list[Token]) -> tuple[str, bool, list[Token]]:
    """(name, highlighted, tokens of the comment) from an item's inline children."""
    while children and children[0].type == "text" and not children[0].content:
        children = children[1:]  # markdown-it leaves empty text tokens around emphasis
    if not children:
        return "", False, []
    first = children[0]
    if first.type == "strong_open":
        end = next(i for i, t in enumerate(children) if t.type == "strong_close")
        name = "".join(t.content for t in children[1:end])
        return name, True, children[end + 1 :]
    if first.type == "code_inline":
        return first.content, False, children[1:]
    name, _, rest = first.content.partition(" ")
    tail = Token("text", "", 0, content=" " + rest) if rest else None
    return name, False, ([tail] if tail else []) + children[1:]


def file_tree(tokens: list[Token], render_inline: Callable[[list[Token]], str]) -> list[Entry]:
    lists: list[list[Entry]] = [[]]  # the list being filled, innermost last
    items: list[Entry] = []  # open list items
    nested: list[bool] = []  # per open bullet list: does it belong to an item?
    for tok in tokens:
        if tok.type == "bullet_list_open":
            nested.append(bool(items))
            if items:
                lists.append(items[-1].children)
        elif tok.type == "bullet_list_close":
            if nested.pop():
                lists.pop()
        elif tok.type == "list_item_open":
            items.append(Entry(""))
            lists[-1].append(items[-1])
        elif tok.type == "list_item_close":
            items.pop()
        elif tok.type == "inline" and items and not items[-1].name:
            name, highlight, rest = _split(tok.children or [])
            items[-1].name, items[-1].highlight = name, highlight
            items[-1].comment = Markup(render_inline(rest).strip())
        elif tok.type in ("paragraph_open", "paragraph_close", "inline") and items:
            continue  # the item's own paragraph
        else:
            raise DokkError(f"a file tree may only contain a bulleted list, not {tok.type}")
    if not lists[0]:
        raise DokkError("a file tree needs a bulleted list")
    return lists[0]
