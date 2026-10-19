import argparse
import logging
import sys
from pathlib import Path

from dokk import DokkError, __version__
from dokk.build import build
from dokk.check import check
from dokk.config import CONFIG_FILE
from dokk.render import base_env
from dokk.writer import SiteWriter

GITIGNORE = ".gitignore"
# Destination -> template in templates/init/.
INIT_FILES = {
    CONFIG_FILE: "init/dokk.toml.jinja",
    "docs/index.md": "init/index.md.jinja",
    GITIGNORE: "init/gitignore.jinja",
    ".github/workflows/docs.yml": "init/docs.yml.jinja",
}


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.root)
    # An existing project has a .gitignore already: dokk's lines are added to it instead.
    existing = [n for n in INIT_FILES if n != GITIGNORE and (root / n).exists()]
    if existing:
        raise DokkError(f"refusing to overwrite: {', '.join(existing)}")
    env = base_env()
    writer = SiteWriter(env, root)
    for name, template in INIT_FILES.items():
        if name == GITIGNORE and (root / name).exists():
            _add_lines(root / name, env.get_template(template).render())
        else:
            writer.render(name, template)
    print(f"Created a dokk site in {root.resolve()}. Run: dokk serve --root {root}")
    return 0


def _add_lines(path: Path, text: str) -> None:
    """Append the lines of `text` that `path` does not have yet."""
    current = path.read_text(encoding="utf-8")
    missing = [line for line in text.splitlines() if line not in current.splitlines()]
    if missing:
        sep = "" if not current or current.endswith("\n") else "\n"
        path.write_text(current + sep + "\n".join(missing) + "\n", encoding="utf-8")


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
        prog="dokk", description="A tiny static docs generator in pure Python."
    )
    parser.add_argument("--version", action="version", version=f"dokk {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    # -v on the commands that build: each build step and how long it took
    verbose = argparse.ArgumentParser(add_help=False)
    verbose.add_argument(
        "-v", "--verbose", action="store_true", help="log each build step and its duration"
    )

    init = sub.add_parser("init", help="scaffold a new site")
    init.add_argument("--root", default=".", help="target directory (default: .)")
    init.set_defaults(func=cmd_init)

    build_cmd = sub.add_parser("build", help="build the site", parents=[verbose])
    build_cmd.add_argument("--root", default=".", help="site root (default: .)")
    build_cmd.add_argument("--drafts", action="store_true", help="include draft pages")
    build_cmd.set_defaults(func=cmd_build)

    serve_cmd = sub.add_parser(
        "serve", help="dev server with live reload (includes drafts)", parents=[verbose]
    )
    serve_cmd.add_argument("--root", default=".", help="site root (default: .)")
    serve_cmd.add_argument("--port", type=int, default=8002, help="port (default: 8002)")
    serve_cmd.add_argument(
        "--search", action="store_true", help="build the search index on every rebuild"
    )
    serve_cmd.set_defaults(func=cmd_serve)

    check_cmd = sub.add_parser("check", help="find broken links, anchors and assets")
    check_cmd.add_argument("--root", default=".", help="site root (default: .)")
    check_cmd.set_defaults(func=cmd_check)
    return parser


def get_log_build_steps() -> None:
    """--verbose: dokk's debug log"""
    logger = logging.getLogger("dokk")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s.%(msecs)03d %(message)s", "%H:%M:%S"))
        logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "verbose", False):
        get_log_build_steps()
    try:
        return args.func(args)
    except DokkError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
