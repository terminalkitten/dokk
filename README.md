<p align="center">
  <a href="https://terminalkitten.github.io/dokk/">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/terminalkitten/dokk/main/public/logo-dark.svg">
      <img src="https://raw.githubusercontent.com/terminalkitten/dokk/main/public/logo.svg" alt="dokk logo" width="72" height="72">
    </picture>
  </a>
</p>

<h1 align="center">dokk</h1>

<p align="center">
  <strong>A tiny static docs generator in pure Python.</strong><br>
  Folders of Markdown in, a fast static docs site out. No Node.
</p>

<p align="center">
  <a href="https://terminalkitten.github.io/dokk/"><strong>Live demo and docs</strong></a> ·
  <a href="https://terminalkitten.github.io/dokk/getting-started/">Quick start</a> ·
  <a href="https://terminalkitten.github.io/dokk/guides/components/">Components</a> ·
  <a href="https://terminalkitten.github.io/dokk/guides/themes/">Themes</a> ·
  <a href="https://terminalkitten.github.io/dokk/guides/themes/showcase/">Theme showcase</a> ·
  <a href="https://pypi.org/project/dokk/">PyPI</a>
</p>

<p align="center">
  <a href="https://terminalkitten.github.io/dokk/guides/writing/">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/terminalkitten/dokk/main/.github/assets/screenshot-dark.png">
      <img src="https://raw.githubusercontent.com/terminalkitten/dokk/main/.github/assets/screenshot-light.png" alt="A dokk site: sidebar, page actions, a file tree and the on-this-page list" width="800">
    </picture>
  </a>
</p>

## Quick start

```sh
pip install "dokk[serve,search]"
dokk init --root my-docs
dokk serve --root my-docs     # http://127.0.0.1:8002/
```

`dokk build` writes plain HTML to `.dokk/build/`, ready for GitHub Pages or any static host.
`dokk init` also creates a workflow that publishes it on every push.

## What you get

- A sidebar built from your folder tree, or arranged in `dokk.toml`.
- Markdown with tables, footnotes, task lists, definition lists and heading anchors.
- Components as Markdown directives: callouts, tabs, cards, steps, file trees, badges and more.
- Code highlighting at build time, in light and dark.
- Full-text search with [Pagefind](https://pagefind.app), fully static.
- Eight [Basecoat](https://basecoatui.com) styles and the shadcn/ui colors, vendored: no CDN, no
  third-party requests.
- `dokk serve` with live reload, and `dokk check` for broken links and anchors.
- A sitemap, a Markdown copy of every page and optional `llms.txt`, for search engines and AI tools.

The [documentation](https://terminalkitten.github.io/dokk/) is built with dokk from the `docs/` folder in this repository.

## Development

Install everything (dev tools, dev server, search, browser tests):

```sh
uv sync --all-extras          # .venv with the exact versions from uv.lock
uv run playwright install chromium   # once, for the browser tests in tests/e2e
```

Run tools through `make` (below) or activate `.venv`. Plain `uv sync` without `--all-extras`
removes the extras again.

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

### Releasing

The version comes from the git tag (hatch-vcs); there is nothing to bump. Push a tag such as
`v0.0.2` and `.github/workflows/release.yml` builds the wheel and sdist and tests the wheel. Once
the `pypi` environment is approved, it publishes to PyPI and creates the GitHub release. CI tests
Linux, macOS and Windows on every push.

### Vendored assets

Basecoat and the shadcn/ui color themes are vendored; see `VENDORED.md`. Update them with
`python scripts/vendor_basecoat.py` and `python scripts/vendor_shadcn_themes.py` (standard library
only, no Node).
