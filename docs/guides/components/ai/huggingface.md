---
title: Hugging Face card
description: A model, dataset or Space on the Hugging Face Hub, linked.
sidebar:
  order: 11
---

`::huggingface[owner/name]` links a repository on the [Hugging Face Hub](https://huggingface.co).
The whole card is a link, with the Hugging Face [logo](model.md#logos). `type` is `model` (the
default), `dataset` or `space`.

```md
::huggingface[meta-llama/Llama-3.1-8B-Instruct]{task="text-generation" params="8B" license="llama3.1"}
```

::huggingface[meta-llama/Llama-3.1-8B-Instruct]{task="text-generation" params="8B" license="llama3.1"}

With a description, as a block:

```md
:::huggingface[HuggingFaceFW/fineweb]{type="dataset" license="odc-by"}
Cleaned and deduplicated English web data from CommonCrawl.
:::
```

:::huggingface[HuggingFaceFW/fineweb]{type="dataset" license="odc-by"}
Cleaned and deduplicated English web data from CommonCrawl.
:::

## Attributes

`type`
: `model`, `dataset` or `space`; it picks the link and the label.

`task`, `params`, `license`, `downloads`, `likes`, `updated`
: Shown with an icon each, as text, such as `downloads="5.1M"`. Builds never fetch them from the
  Hub, so they stay what you write.
