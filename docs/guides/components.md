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

### Synced tabs

Give tab sets the same `sync` key and they switch together. The reader's choice is remembered
on every page.

```md
::::tabs{sync="pkg"}
:::tab[pip]
`pip install dokk`
:::
:::tab[uv]
`uv pip install dokk`
:::
::::
```

::::tabs{sync="pkg"}
:::tab[pip]
`pip install dokk`
:::
:::tab[uv]
`uv pip install dokk`
:::
::::

::::tabs{sync="pkg"}
:::tab[pip]
`pip install "dokk[search]"`
:::
:::tab[uv]
`uv pip install "dokk[search]"`
:::
::::

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

## Details

A collapsible block. The title is the summary, "Details" by default.

```md
:::details[Show the full config]
Anything in Markdown.
:::
```

:::details[Show the full config]
Anything in Markdown.
:::

## Badges

Inline, inside any text: `:badge[Text]`, with an optional `variant`: `default`, `secondary`,
`outline` or `danger`.

```md
Search :badge[New] works offline :badge[Beta]{variant="secondary"}.
```

Search :badge[New] works offline :badge[Beta]{variant="secondary"}.

## File tree

A bulleted list inside `:::filetree`. A nested list or a trailing `/` makes a folder, `**bold**`
highlights an entry, text after the name is a comment, and `…` is a placeholder. Use backticks
for names with spaces or underscores.

```md
:::filetree
- dokk.toml
- **docs**
  - index.md the home page
  - guides/
  - …
- `my file.txt`
:::
```

:::filetree
- dokk.toml
- **docs**
  - index.md the home page
  - guides/
  - …
- `my file.txt`
:::

## Link buttons

A one-line directive (two colons). Variants: `primary` (default), `secondary` and `minimal`.
External links get an arrow.

```md
::linkbutton[Get started]{href="../getting-started/index.md"}
::linkbutton[Basecoat]{href="https://basecoatui.com" variant="secondary"}
::linkbutton[Pagefind]{href="https://pagefind.app" variant="minimal"}
```

::linkbutton[Get started]{href="../getting-started/index.md"}
::linkbutton[Basecoat]{href="https://basecoatui.com" variant="secondary"}
::linkbutton[Pagefind]{href="https://pagefind.app" variant="minimal"}

An unknown directive name fails the build with the file and line number.
