---
title: Tabs
description: Switch between versions of the same content, optionally synced across the site.
sidebar:
  order: 2
---

Put alternatives for the same thing side by side, such as install commands or languages.
Each `:::tab[label]` inside `::::tabs` is one tab.

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

## Synced tabs

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
