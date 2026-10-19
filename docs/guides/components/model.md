---
title: Model card
description: An AI model with its prices, context window, limits and features.
sidebar:
  order: 10
---

`:::model[Name]` shows an AI model with its provider, API name, prices and limits. Every
attribute is optional, the body is a description in Markdown. Use a one-line `::model[Name]{...}`
without a description.

```md
:::model[Acme Large 2]{provider="Acme AI" model="acme-large-2" input="3" output="15" cached="0.30" context="200K" max_output="64K" cutoff="2026-03" features="text vision tools reasoning"}
Our most capable model, for **complex** coding and analysis.
:::
```

:::model[Acme Large 2]{provider="Acme AI" model="acme-large-2" input="3" output="15" cached="0.30" context="200K" max_output="64K" cutoff="2026-03" features="text vision tools reasoning"}
Our most capable model, for **complex** coding and analysis.
:::

Without a description, as one line:

```md
::model[Acme Open 7B]{provider="Acme AI" context="32K" license="Apache-2.0" released="2026-01" features="text code json"}
```

::model[Acme Open 7B]{provider="Acme AI" context="32K" license="Apache-2.0" released="2026-01" features="text code json"}

## Attributes

`provider`, `model`
: The provider, and the model name to use in API calls.

`input`, `output`, `cached`
: Prices per million tokens for input, output and cached input. A plain number gets a `$`;
  write `€2` or `free` for anything else.

`context`, `max_output`
: The context window and the most tokens in one answer, such as `200K` or `1M`.

`cutoff`, `released`, `license`
: The knowledge cutoff (shown as Cutoff), the release date and the license, as text.

`features`
: Words separated by spaces, shown as badges. These get an icon: `text`, `vision`, `image`,
  `audio`, `video`, `tools`, `reasoning`, `code`, `json`, `search`, `streaming`, `files` and
  `caching`. Other words are shown without one.

`src`, `href`
: A logo image instead of the robot icon, and a link to the model's docs. Both are relative to
  the page, like Markdown links.

:::note
The card shows what you write: builds never fetch prices, so update them when the provider does.
:::
