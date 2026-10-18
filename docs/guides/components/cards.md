---
title: Cards
description: A grid of cards, optionally linking to other pages.
sidebar:
  order: 3
---

Wrap `:::card[title]` blocks in `::::cards` for a grid. With `href`, the whole card is a link.

```md
::::cards
:::card[Get started]{href="../../getting-started/index.md"}
Install and build your first site.
:::
::::
```

::::cards
:::card[Get started]{href="../../getting-started/index.md"}
Install and build your first site.
:::
:::card[No link]
Cards without `href` are not clickable.
:::
::::
