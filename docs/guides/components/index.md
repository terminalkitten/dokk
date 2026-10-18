---
title: Components
description: Callouts, tabs, cards, steps and more, written as Markdown directives.
sidebar:
  order: 2
---

Components are written as directives: a fence of colons, a name, an optional `[title]` and
optional `{key="value"}` attributes. They become static HTML at build time, with no JavaScript
needed to show them.

```md
:::note[A title]
Any **Markdown** inside.
:::
```

Block components use three colons and a closing fence. One-line components, like link buttons,
use two. Inline ones, like badges, use one. To put a component inside another, give the outer
fence more colons. An unknown name fails the build with the file and line number.

::::cards
:::card[Callouts]{href="callouts.md"}
Notes, tips, cautions and warnings.
:::
:::card[Tabs]{href="tabs.md"}
Alternatives side by side, synced across pages.
:::
:::card[Cards]{href="cards.md"}
A grid of cards, optionally linked.
:::
:::card[Steps]{href="steps.md"}
A numbered sequence of steps.
:::
:::card[Details]{href="details.md"}
A collapsible block.
:::
:::card[File tree]{href="file-tree.md"}
A folder structure from a bulleted list.
:::
:::card[Link buttons]{href="link-buttons.md"}
Links styled as buttons.
:::
:::card[Badges, keys and colors]{href="inline.md"}
Inline badges, keyboard keys and color swatches.
:::
::::
