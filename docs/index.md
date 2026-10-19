---
title: dokk
description: A tiny static docs generator in Python. Markdown folders in, a fast static site out.
sidebar:
  label: Introduction
---

dokk turns a folder of Markdown files into a documentation site with a sidebar menu, search, dark mode and
code highlighting. Everything is rendered at build time, so the output is plain HTML that works on GitHub
Pages or any static host.

::::cards
:::card[Get started]{href="getting-started/index.md"}
Install dokk and build your first site in a minute.
:::

:::card[Write pages]{href="guides/writing.md"}
Front matter, the sidebar, links and images.
:::

:::card[Components]{href="guides/components/index.md"}
Callouts, tabs, cards and steps, straight from Markdown.
:::

:::card[Deploy]{href="guides/deploy.md"}
Publish to GitHub Pages with the generated workflow.
:::
::::

## What you get

- A sidebar built from your folder tree, with the current page highlighted.
- Markdown with tables, footnotes, task lists, definition lists and heading anchors.
- Code highlighting at build time, in light and dark.
- Full-text search with [Pagefind](https://pagefind.app), fully static.
- `dokk serve` with live reload and `dokk check` for broken links.
- UI from [Basecoat](https://basecoatui.com), vendored: no CDN, no third-party requests.
