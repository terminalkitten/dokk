---
title: Components
sidebar:
  order: 2
---

Directives turn into static HTML at build time.

## Callouts

:::note
A note with the default title.
:::

:::tip[Pro tip]
Callouts can hold **Markdown**, `code` and [links](../getting-started/install.md).
:::

:::caution
Careful now.
:::

:::danger[Do not <script>]
Titles are escaped.
:::

## Tabs

::::tabs
:::tab[pip]
```sh
pip install dokk
```
:::
:::tab[uv]
```sh
uv pip install dokk
```
:::
::::

A second tab set gets its own id. Nesting needs more colons on each outer fence:

:::::tabs
::::tab[One]
First panel.
::::
::::tab[Two]
:::note
Directives nest inside tabs.
:::
::::
:::::

## Cards

::::cards
:::card[Quick start]{href="../getting-started/index.md"}
Install and build your first site.
:::
:::card[Writing]{href="/guides/writing/"}
Pages, links and images.
:::
:::card[No link]
A plain card.
:::
::::

## Steps

:::steps
1. Install dokk.
2. Run `dokk init`.
3. Run `dokk build` and open `dist/`.
:::
