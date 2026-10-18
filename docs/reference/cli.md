---
title: Command line
description: dokk init, build, serve and check.
sidebar:
  order: 1
---

Every command takes `--root PATH`, the folder with `dokk.toml` (default: the current folder).

| Command | What it does |
|---|---|
| `dokk init` | Scaffold `dokk.toml`, `docs/index.md`, `.gitignore` and a Pages workflow. Never overwrites files. |
| `dokk build [--drafts]` | Build the site into `out_dir`. Prints broken links as warnings. |
| `dokk serve [--port 8000] [--search]` | Dev server with live reload. Includes drafts, ignores the base path. `--search` rebuilds the search index too. |
| `dokk check` | Build into a temporary folder and report broken links, missing anchors and assets. Exits 1 on errors, for CI. |
