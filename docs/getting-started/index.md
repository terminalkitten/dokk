---
title: Getting started
description: Install dokk, create a site and preview it locally.
sidebar:
  order: 1
  label: Quick start
---

## Install

dokk needs Python 3.11 or newer.

::::tabs
:::tab[pip]
```sh
pip install "dokk[serve,search]"
```
:::
:::tab[uv]
```sh
uv pip install "dokk[serve,search]"
```
:::
::::

The `serve` extra adds the dev server, `search` adds the Pagefind index. Both are optional.

## Create a site

:::steps
1. Scaffold a site in a new folder:

   ```sh
   dokk init --root my-docs
   ```

2. Start the dev server and open <http://127.0.0.1:8000/>:

   ```sh
   dokk serve --root my-docs
   ```

3. Edit `my-docs/docs/index.md`. The browser reloads when you save.

4. Build the production site into `my-docs/dist/`:

   ```sh
   dokk build --root my-docs
   ```
:::

`dokk init` creates `dokk.toml`, `docs/index.md`, a `.gitignore` and a GitHub Pages workflow.

:::tip
Run `dokk check` before you publish. It finds broken links, missing anchors and missing images.
:::
