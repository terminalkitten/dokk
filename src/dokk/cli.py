import argparse
import sys
from pathlib import Path

from dokk import DokkError, __version__
from dokk.build import build
from dokk.config import CONFIG_FILE

_INIT_FILES = {
    CONFIG_FILE: 'title = "My docs"\n# site_url = "https://example.github.io/my-docs/"\n',
    "docs/index.md": "---\ntitle: Welcome\n---\n\nStart writing in `docs/`.\n",
    ".gitignore": "dist/\n",
}


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.root)
    existing = [name for name in _INIT_FILES if (root / name).exists()]
    if existing:
        raise DokkError(f"refusing to overwrite: {', '.join(existing)}")
    for name, text in _INIT_FILES.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(f"Created a dokk site in {root.resolve()}. Run: dokk build --root {root}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    cfg = build(Path(args.root), drafts=args.drafts)
    print(f"Built {cfg.out_dir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dokk", description="Small static documentation generator."
    )
    parser.add_argument("--version", action="version", version=f"dokk {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="scaffold a new site")
    init.add_argument("--root", default=".", help="target directory (default: .)")
    init.set_defaults(func=cmd_init)

    build_cmd = sub.add_parser("build", help="build the site")
    build_cmd.add_argument("--root", default=".", help="site root (default: .)")
    build_cmd.add_argument("--drafts", action="store_true", help="include draft pages")
    build_cmd.set_defaults(func=cmd_build)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except DokkError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
