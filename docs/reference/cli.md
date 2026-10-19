---
title: Command line
description: dokk init, build, serve, check and format, with every option.
sidebar:
  order: 1
---

```sh title="Terminal"
dokk init     # scaffold a new site
dokk serve    # write with live reload
dokk check    # find broken links before you publish
dokk format   # tidy the Markdown of every page
dokk build    # build the production site
```

Every command takes `--root PATH`, the folder with `dokk.toml`; it defaults to the current folder.
`dokk --version` prints the version.

## dokk init

Scaffolds a new site in `--root`.

:::filetree
- dokk.toml title and settings
- docs/
  - index.md the home page
- .gitignore ignores .dokk/
- .github/
  - workflows/
    - docs.yml builds and deploys to GitHub Pages
:::

`--root PATH`
: Where to create the site. Default: the current folder.

:::note
`init` never overwrites. If any of these files exist, it stops and lists them. The exception is
`.gitignore`: in an existing project, `init` adds `.dokk/` to it.
:::

## dokk serve

Builds into `.dokk/dev/`, serves it and rebuilds when you save. The browser reloads on its own.
Stop it with :kbd[Ctrl+C].

```sh title="Terminal"
dokk serve --port 8001 --search
```

`--port PORT`
: Port on `127.0.0.1`. Default: `8002`.

`--search`
: Build the search index on every rebuild. Off by default, because indexing makes rebuilds slower.

`-v`, `--verbose`
: Log each step of every rebuild and how long it took, as `dokk build -v` does.

`--root PATH`
: The site folder. Default: the current folder.

Draft pages are included, and the base path from `site_url` is ignored, so links work on
`localhost`. A build error shows in the browser and clears on the next good save.

:::caution
`serve` is for writing, not hosting. Publish the output of `dokk build`.
:::

## dokk check

Builds the production site into a temporary folder and reports problems:

- links to missing pages, files or anchors
- pages without a title, more than one `<h1>`, or skipped heading levels
- with `[[sidebar]]` in `dokk.toml`: pages missing from the sidebar

```sh title="Terminal"
dokk check
```

`--root PATH`
: The site folder. Default: the current folder.

:::tip
`check` exits with status 1 when it finds errors, so it can stop a CI run. The workflow from
`dokk init` runs it before every deploy.
:::

## dokk build

Builds the production site into `out_dir` (default `.dokk/build/`), with the search index when the
search extra is installed. Broken links are printed as warnings.

```sh title="Terminal"
dokk build --drafts
```

`--drafts`

: Include pages with `draft: true`.

`-v`, `--verbose`

: Log each build step when it starts and how long it took, to find what makes a build slow:

  ```text
  19:36:12.582 markdown (44 pages) ...
  19:36:13.000 markdown (44 pages): 418 ms
  19:36:13.000 write pages ...
  19:36:13.152 write pages: 152 ms
  ```

`--root PATH`

: The site folder. Default: the current folder.

Builds are deterministic: the same input gives byte-identical output. When `site_url` has no path,
you can look at a build locally with `python -m http.server 8000 -d .dokk/build`. With a path,
such as GitHub Pages' `/my-docs/`, links only work once deployed; use `dokk serve` locally.

## dokk format

Formats every page in the content folder with [mdformat](https://github.com/hukkin/mdformat), so
lists, tables and spacing look the same everywhere. It knows dokk's Markdown: front matter,
components, tables, footnotes and definition lists are kept intact, and the lines in `:::env` and
`:::bench` stay exactly as written.

```sh title="Terminal"
pip install "dokk[format]"
dokk format
```

`--check`
: Change nothing; list the pages that are not formatted and exit with an error. Use it in CI or a
  pre-commit hook.

`--root PATH`
: The site folder. Default: the current folder.
