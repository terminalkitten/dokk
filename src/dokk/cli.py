import argparse
import sys

from dokk import __version__


def _not_implemented(args: argparse.Namespace) -> int:
    print(f"dokk {args.command}: not implemented yet", file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dokk", description="Small static documentation generator."
    )
    parser.add_argument("--version", action="version", version=f"dokk {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="scaffold a new site")
    init.set_defaults(func=_not_implemented)

    build = sub.add_parser("build", help="build the site")
    build.add_argument("--root", default=".", help="site root (default: .)")
    build.add_argument("--drafts", action="store_true", help="include draft pages")
    build.set_defaults(func=_not_implemented)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)
