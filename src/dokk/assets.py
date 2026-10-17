import shutil
from pathlib import Path

STATIC = Path(__file__).parent / "static"
ASSETS_DIR = "_dokk"  # package static files land in <out>/_dokk/


def copy_static(out: Path) -> None:
    shutil.copytree(STATIC, out / ASSETS_DIR)


def copy_public(root: Path, out: Path) -> None:
    public = root / "public"
    if public.is_dir():
        shutil.copytree(public, out, dirs_exist_ok=True)


def copy_page_assets(content_dir: Path, out: Path) -> None:
    """Copy every non-Markdown file under content_dir to the same relative path."""
    for src in sorted(content_dir.rglob("*")):
        rel = src.relative_to(content_dir)
        if src.is_file() and src.suffix != ".md" and not any(p.startswith(".") for p in rel.parts):
            dest = out / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
