import argparse
import sys
from pathlib import Path

from dokk import DokkError, __version__
from dokk.build import build
from dokk.check import check
from dokk.config import CONFIG_FILE
from dokk.render import base_env
from dokk.writer import SiteWriter

# Destination -> template in templates/init/.
INIT_FILES = {
    CONFIG_FILE: "init/dokk.toml.jinja",
    "docs/index.md": "init/index.md.jinja",
    ".gitignore": "init/gitignore.jinja",
    ".github/workflows/docs.yml": "init/docs.yml.jinja",
}


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.root)
    existing = [name for name in INIT_FILES if (root / name).exists()]
    if existing:
        raise DokkError(f"refusing to overwrite: {', '.join(existing)}")
    writer = SiteWriter(base_env(), root)
    for name, template in INIT_FILES.items():
        writer.render(name, template)
    print(f"Created a dokk site in {root.resolve()}. Run: dokk serve --root {root}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    result = build(Path(args.root), drafts=args.drafts, parallel=True)
    for rel, hrefs in result.broken.items():
        for href in hrefs:
            print(f"warning: {rel.as_posix()}: broken link {href!r}", file=sys.stderr)
    if result.search_missing:
        print(
            "warning: search is enabled but pagefind is not installed: pip install 'dokk[search]'",
            file=sys.stderr,
        )
    print(f"Built {result.out_dir}" + (" (with search index)" if result.search else ""))
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    from dokk.serve import serve

    serve(Path(args.root), port=args.port, search=args.search)
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    issues = check(Path(args.root))
    for issue in issues:
        print(issue, file=sys.stderr)
    errors = sum(i.level == "error" for i in issues)
    warnings = len(issues) - errors
    print(f"{errors} error(s), {warnings} warning(s)")
    return 1 if errors else 0


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

    serve_cmd = sub.add_parser("serve", help="dev server with live reload (includes drafts)")
    serve_cmd.add_argument("--root", default=".", help="site root (default: .)")
    serve_cmd.add_argument("--port", type=int, default=8000, help="port (default: 8000)")
    serve_cmd.add_argument(
        "--search", action="store_true", help="build the search index on every rebuild"
    )
    serve_cmd.set_defaults(func=cmd_serve)

    check_cmd = sub.add_parser("check", help="find broken links, anchors and assets")
    check_cmd.add_argument("--root", default=".", help="site root (default: .)")
    check_cmd.set_defaults(func=cmd_check)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except DokkError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
