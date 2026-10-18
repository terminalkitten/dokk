---
title: Components
description: Callouts, tabs, cards and steps written as Markdown directives.
sidebar:
  order: 2
---

Components are written as directives: a fence of colons, a name, an optional `[title]` and optional
`{key="value"}` attributes. They become static HTML at build time.

## Callouts

```md
:::note
The default title is the type.
:::

:::tip[Custom title]
Callouts hold any **Markdown**.
:::
```

:::note
The default title is the type.
:::

:::tip[Custom title]
Callouts hold any **Markdown**.
:::

:::caution
Also available: `caution`.
:::

:::danger
And `danger`.
:::

## Tabs

```md
::::tabs
:::tab[pip]
`pip install dokk`
:::
:::tab[uv]
`uv pip install dokk`
:::
::::
```

::::tabs
:::tab[pip]
`pip install dokk`
:::
:::tab[uv]
`uv pip install dokk`
:::
::::

:::note[Nesting]
An outer fence needs more colons than the one inside it, as with `::::tabs` around `:::tab`.
:::

## Cards

```md
::::cards
:::card[Get started]{href="../getting-started/index.md"}
Install and build your first site.
:::
::::
```

::::cards
:::card[Get started]{href="../getting-started/index.md"}
Install and build your first site.
:::
:::card[No link]
Cards without `href` are not clickable.
:::
::::

## Steps

```md
:::steps
1. Install dokk.
2. Run `dokk init`.
:::
```

:::steps
1. Install dokk.
2. Run `dokk init`.
:::

An unknown directive name fails the build with the file and line number.
