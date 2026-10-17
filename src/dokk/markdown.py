from markdown_it import MarkdownIt


def make_md() -> MarkdownIt:
    # ponytail: minimal for Phase 1; plugins, highlighting and TOC arrive in Phase 2.
    return MarkdownIt("commonmark", {"html": True}).enable(["table", "strikethrough"])


def render_markdown(md: MarkdownIt, body: str) -> str:
    return md.render(body)
