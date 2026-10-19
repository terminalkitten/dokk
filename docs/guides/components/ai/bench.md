---
title: Benchmark
description: Benchmark scores as bars, with your model highlighted.
sidebar:
  order: 8
---

`:::bench[Title]` draws a bar for every `Label: score` line. Bars are relative to `max`, or to
the best score without it; `highlight` picks out one line.

```md
:::bench[Made-up eval, accuracy]{max="100" highlight="Acme Large 2"}
Acme Large 2: 88.4%
Acme Small 2: 79.1%
Baseline: 61.0%
:::
```

:::bench[Made-up eval, accuracy]{max="100" highlight="Acme Large 2"}
Acme Large 2: 88.4%
Acme Small 2: 79.1%
Baseline: 61.0%
:::

The score is a number, optionally followed by a unit such as `%` or `ms`. Bars are plain CSS: no
JavaScript, no chart library.
