import subprocess
from datetime import date
from pathlib import Path

from dokk.content import Page


def last_modified(content_dir: Path, pages: list[Page]) -> dict[Path, date]:
    """Last commit date per page (one `git log` call), else the file's mtime."""
    dates: dict[Path, date] = {}
    try:
        out = subprocess.run(
            ["git", "-c", "core.quotePath=false", "-C", str(content_dir), "log",
             "--format=%x00%cs", "--name-only", "--relative", "--", "."],
            capture_output=True, encoding="utf-8", check=True,
        ).stdout  # fmt: skip
    except (OSError, subprocess.CalledProcessError):
        out = ""
    current: date | None = None
    for line in out.splitlines():
        if line.startswith("\x00"):
            current = date.fromisoformat(line[1:])
        elif line and current:
            dates.setdefault(Path(line), current)  # newest commit comes first
    return {p.rel: dates.get(p.rel) or date.fromtimestamp(p.src.stat().st_mtime) for p in pages}
