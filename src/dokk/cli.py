import argparse
import sys
from pathlib import Path

from dokk import DokkError, __version__
from dokk.build import build
from dokk.check import check
from dokk.config import CONFIG_FILE

_WORKFLOW = """\
name: Docs

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.13"
      - run: pip install dokk
      - run: dokk check
      - run: dokk build
      - uses: actions/configure-pages@v6
      - uses: actions/upload-pages-artifact@v5
        with:
          path: dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v5
"""

_INIT_FILES = {
    CONFIG_FILE: 'title = "My docs"\n# site_url = "https://example.github.io/my-docs/"\n',
    "docs/index.md": "---\ntitle: Welcome\n---\n\nStart writing in `docs/`.\n",
    ".gitignore": "dist/\n.dokk/\n",
    ".github/workflows/docs.yml": _WORKFLOW,
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
    print(f"Created a dokk site in {root.resolve()}. Run: dokk serve --root {root}")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    result = build(Path(args.root), drafts=args.drafts)
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
