---
title: Model release
description: Release notes for a made-up model, with its card, benchmarks and weights.
sidebar:
  order: 3
---

**Acme Large 2** is out today, with a bigger context window and better tool use. The model, the
numbers and the links on this page are made up. :badge[Example]{variant="secondary"}

:::model[Acme Large 2]{provider="Acme AI" model="acme-large-2" input="3" output="15" cached="0.30" context="200K" max_output="64K" cutoff="2026-03" released="2026-10" features="text vision tools reasoning json caching"}
Our most capable model, for **complex** coding, analysis and long documents.
:::

## Benchmarks

:::bench[Code eval, pass@1]{max="100" highlight="Acme Large 2"}
Acme Large 2: 88.4%
Acme Large 1: 81.0%
Acme Small 2: 72.5%
Acme Open 7B: 48.2%
:::

:::bench[Median latency, first token]{highlight="Acme Large 2"}
Acme Large 2: 420ms
Acme Large 1: 610ms
Acme Small 2: 180ms
:::

:::note
For latency, shorter bars are better. Our evals and their settings are in the technical report.
:::

## The family

::::models
::model[Acme Large 2]{provider="Acme AI" model="acme-large-2" input="3" output="15" context="200K" max_output="64K" features="text vision tools reasoning"}

::model[Acme Small 2]{provider="Acme AI" model="acme-small-2" input="0.25" output="1.25" context="200K" max_output="16K" features="text tools"}

::model[Acme Open 7B]{provider="Acme AI" context="32K" license="Apache-2.0" released="2026-01" features="text code"}
::::

## Try it

::install[acme-sdk]

```python
from acme import Acme

client = Acme()
reply = client.chat(model="acme-large-2", message="Hi!")
print(reply.text)
```

::::chat
:::system
Answer in one sentence.
:::

:::user
What is new in Acme Large 2?
:::

:::assistant[Acme Large 2]
A 200K context window, better tool use and prompt caching, at the same price as before.
:::
::::

## Open weights

The small open model and its training data are on the Hugging Face Hub.

:::huggingface[acme-ai/acme-open-7b]{task="text-generation" params="7B" license="apache-2.0" downloads="1.2M" likes="3.4K"}
The open 7B model, for local use and fine-tuning.
:::

::huggingface[acme-ai/acme-mix]{type="dataset" license="odc-by" updated="2026-09"}
