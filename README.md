<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/terminalkitten/dokk/main/public/logo-dark.svg">
    <img src="https://raw.githubusercontent.com/terminalkitten/dokk/main/public/logo.svg" alt="" width="32" height="32">
  </picture>
  dokk
</h1>

A small static documentation generator. Folders of Markdown become a fast static site with a
sidebar, search, dark mode and code highlighting, styled with [Basecoat](https://basecoatui.com).
No Node needed to build.

```sh
pip install "dokk[serve,search]"
dokk init --root my-docs
dokk serve --root my-docs
```

The full documentation lives in `docs/` and is built with dokk itself.

## Development

Install everything (dev tools, dev server, search, browser tests):

```sh
uv pip install -e ".[dev,serve,search,e2e]"
playwright install chromium   # once, for the browser tests in tests/e2e
```

Run the checks:

```sh
make lint        # all of the below
make format      # ruff: fix lint issues, then format
make typecheck   # ty
make test        # pytest
```

### Serving the sites

The repo has two sites. Without `--root`, dokk uses the current folder.

| Site | What it is | Serve it with |
|---|---|---|
| `docs/` | dokk's own documentation | `dokk serve --port 8001 --search` |
| `examples/basic/` | Acme Widgets, a fictional site that uses every feature and component; the fixture for the tests | `dokk serve --root examples/basic --port 8002 --search` |

`dokk serve` rebuilds on every change and reloads the browser. It includes draft pages and
ignores the base path; `--search` also rebuilds the search index.

To look at a production build instead:

```sh
dokk build --root examples/basic
python -m http.server 8002 -d examples/basic/.dokk/build
```

### Vendored assets

Basecoat and the shadcn/ui color themes are vendored; see `VENDORED.md`. Update them with
`python scripts/vendor_basecoat.py` and `python scripts/vendor_shadcn_themes.py` (standard library
only, no Node).
