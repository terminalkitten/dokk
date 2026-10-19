---
title: LLM client library
description: The quickstart of a made-up Python client for several LLM providers.
sidebar:
  order: 1
---

**quill** is a small Python client that talks to several model providers through one API. This
page is its quickstart. :badge[Example]{variant="secondary"}

## Install

::install[quill-llm]

Optional extras add a provider's own SDK for streaming and batch jobs:

::install[quill-llm[anthropic,openai]]{tools="uv pip"}

## Configure

quill reads its settings from the environment, or from a `.env` file in the working folder.
Set the key for each provider you use.

:::env
ANTHROPIC_API_KEY=                 # Key for Claude models.
OPENAI_API_KEY=                    # Key for GPT models.
QUILL_DEFAULT_MODEL=claude-sonnet  # Used when a call names no model.
QUILL_TIMEOUT=60                   # Seconds before a request gives up.
QUILL_LOG_LEVEL=warning            # debug, info, warning or error.
:::

:::caution
Never commit `.env`. Add it to `.gitignore` before you put a key in it.
:::

## Your first call

::::tabs{sync="lang"}
:::tab[Sync]
```python
from quill import Client

client = Client()
reply = client.chat("Explain recursion in one sentence.")
print(reply.text)
```
:::
:::tab[Async]
```python
import asyncio
from quill import AsyncClient

async def main() -> None:
    client = AsyncClient()
    reply = await client.chat("Explain recursion in one sentence.")
    print(reply.text)

asyncio.run(main())
```
:::
::::

What the call sends, and what comes back:

::::chat
:::user
Explain recursion in one sentence.
:::
:::assistant[claude-sonnet]{icon="claude"}
Recursion is when a function solves a problem by calling itself on a smaller piece of the same
problem, until the piece is small enough to answer directly.
:::
::::

## Supported providers

Pick a model by its name, such as `client.chat(..., model="gpt-mini")`. quill maps it to the
provider's API name.

::::models
::model[claude-sonnet]{provider="Anthropic" icon="claude" context="200K" features="text vision tools streaming"}
::model[gpt-mini]{provider="OpenAI" icon="openai" context="128K" features="text vision tools json"}
::model[mistral-small]{provider="Mistral AI" icon="mistralai" context="32K" license="Apache-2.0" features="text tools"}
::model[llama-local]{provider="Ollama" icon="ollama" context="8K" input="free" output="free" features="text"}
::::

:::note
Prices and limits change often; quill's docs leave them to each provider's pricing page.
:::

## Next

::linkbutton[Agent framework example]{href="agent.md"}
::linkbutton[All components]{href="../../guides/components/index.md" variant="secondary"}
