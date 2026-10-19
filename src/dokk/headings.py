"""Attributes at the end of a heading: `## Install { #setup .wide }`, as MkDocs' attr_list
writes them (spaces inside the braces are optional). The block is removed from the heading text
and its id, classes and key="value" pairs go on the heading; a custom id replaces the generated
one, permalink included.
"""

import re

from markdown_it import MarkdownIt
from markdown_it.rules_core import StateCore

_PART = r'(?:[#.][\w-]+|[\w-]+=(?:"[^"]*"|[^\s"}]+))'
TRAILING_ATTRS = re.compile(rf"\s*\{{:?\s*({_PART}(?:\s+{_PART})*)\s*\}}\s*$")
_ITEM = re.compile(r'([#.])([\w-]+)|([\w-]+)=(?:"([^"]*)"|([^\s"}]+))')


def strip_attrs(text: str) -> str:
    """Heading or title text without its trailing attribute block."""
    return TRAILING_ATTRS.sub("", text)


def _take_attrs(state: StateCore) -> None:
    for i, token in enumerate(state.tokens):
        if token.type != "heading_open":
            continue
        children = state.tokens[i + 1].children or []
        last = children[-1] if children else None
        match = TRAILING_ATTRS.search(last.content) if last and last.type == "text" else None
        if not (last and match):
            continue
        last.content = last.content[: match.start()]
        classes = []
        for mark, name, key, quoted, bare in _ITEM.findall(match.group(1)):
            if mark == "#":
                token.meta["custom_id"] = name
            elif mark == ".":
                classes.append(name)
            else:
                token.attrSet(key, quoted or bare)
        if classes:
            token.attrSet("class", " ".join(classes))


def _apply_ids(state: StateCore) -> None:
    for i, token in enumerate(state.tokens):
        custom = token.meta.get("custom_id") if token.type == "heading_open" else None
        if not custom:
            continue
        token.attrSet("id", custom)
        for child in state.tokens[i + 1].children or []:  # the permalink the anchors plugin added
            if child.type == "link_open" and child.attrGet("class") == "header-anchor":
                child.attrSet("href", f"#{custom}")


def heading_attrs_plugin(md: MarkdownIt) -> None:
    """Use after the anchors plugin. The attributes are read right after inline parsing, before
    the typographer turns their quotes curly; the ids are set after the anchors plugin."""
    md.core.ruler.after("inline", "heading_attrs", _take_attrs)
    md.core.ruler.after("anchor", "heading_ids", _apply_ids)
