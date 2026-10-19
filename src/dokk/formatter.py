"""`dokk format`: mdformat over the content folder, with the plugins that keep dokk's Markdown
intact: front matter, GitHub tables, footnotes, definition lists and directives."""

from pathlib import Path

from dokk import DokkError
from dokk.content import is_hidden

EXTENSIONS = ("frontmatter", "gfm", "footnote", "deflist", "directives")
OPTIONS = {
    "number": True,  # keep lists numbered 1. 2. 3.
    "plugin": {"directives": {"raw": ["env", "bench"]}},  # their bodies are data, not Markdown
}


def format_docs(content_dir: Path, check: bool = False) -> list[Path]:
    """Format every page in place; with `check`, change nothing. Returns the pages that were
    (or, with `check`, would be) changed, relative to content_dir."""
    try:
        import mdformat
    except ImportError:
        raise DokkError("dokk format needs the format extra: pip install 'dokk[format]'") from None
    changed = []
    for src in sorted(content_dir.rglob("*.md")):
        rel = src.relative_to(content_dir)
        if not src.is_file() or is_hidden(rel):
            continue
        text = src.read_text(encoding="utf-8")
        try:
            formatted = mdformat.text(text, options=OPTIONS, extensions=EXTENSIONS)
        except Exception as e:  # a missing plugin, or output that would render differently
            raise DokkError(f"{rel}: cannot format: {e}") from None
        if formatted != text:
            changed.append(rel)
            if not check:
                src.write_text(formatted, encoding="utf-8")
    return changed
