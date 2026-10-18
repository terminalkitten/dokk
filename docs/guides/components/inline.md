---
title: Badges, keys and colors
description: Badges, keyboard keys and color swatches inside any text.
sidebar:
  order: 8
---

These work inside any text, including headings, lists and tables.

## Badges

Inline, inside any text: `:badge[Text]`, with an optional `variant`: `default`, `secondary`,
`outline` or `danger`.

```md
Search :badge[New] works offline :badge[Beta]{variant="secondary"}.
```

Search :badge[New] works offline :badge[Beta]{variant="secondary"}.

## Keys

`:kbd[...]` shows a keyboard key.

```md
Open search with :kbd[Ctrl+K].
```

Open search with :kbd[Ctrl+K].

## Color swatches

`:swatch[...]` shows a small chip of any CSS color: a hex value, a name or a function such as
`oklch()`. The color is also its accessible name.

```md
The brand pink is :swatch[#db2777] `#db2777`.
```

The brand pink is :swatch[#db2777] `#db2777`.
