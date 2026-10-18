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
        text=True,
    )
    if proc.returncode:
        raise DokkError(f"pagefind failed:\n{(proc.stderr or proc.stdout).strip()}")
