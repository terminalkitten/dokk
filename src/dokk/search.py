import importlib.util
import subprocess
import sys
from pathlib import Path

from dokk import DokkError


def search_available() -> bool:
    return importlib.util.find_spec("pagefind") is not None


def build_index(out: Path) -> None:
    """Run Pagefind over the built site; the bundle lands in <out>/pagefind/."""
    proc = subprocess.run(
        [sys.executable, "-m", "pagefind", "--site", str(out), "--silent"],
        capture_output=True,
        encoding="utf-8",
        errors="replace",  # only shown in an error message
    )
    if proc.returncode:
        raise DokkError(f"pagefind failed:\n{(proc.stderr or proc.stdout).strip()}")
