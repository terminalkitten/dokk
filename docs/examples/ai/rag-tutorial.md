---
title: RAG tutorial
description: A tutorial that answers questions about your own documents, step by step.
sidebar:
  order: 4
---

:::note[Example page]
The project, data and links on this page are made up, to show what dokk's components can do. It
does not document dokk itself.
:::

In this tutorial you build a small app that answers questions about your own Markdown files:
it finds the relevant passages and asks a model to answer from them only. This is
**retrieval-augmented generation**, RAG for short.

## What you need

:::steps
1. Python 3.11 or newer.
2. An API key for a model provider.
3. A folder of Markdown files to ask questions about.
:::

## Set up the project

::install[sentence-transformers]

It brings NumPy along. Then put your settings in `.env`:

:::env
OPENAI_API_KEY=                    # For the answering model.
DOCS_DIR=./notes                   # The Markdown files to search.
TOP_K=4                            # How many passages go into the prompt.
:::

When you are done, the project looks like this:

:::filetree
- .env
- **app.py** the whole app
- notes/
  - …
:::

## Embed your documents

An embedding model turns each passage into a vector; similar passages get similar vectors. This
tutorial uses a small one that runs on a laptop:

::huggingface[sentence-transformers/all-MiniLM-L6-v2]{task="sentence-similarity" params="22.7M" license="apache-2.0"}

```python title="app.py"
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
passages = [p for f in Path("notes").glob("*.md") for p in f.read_text().split("\n\n")]
vectors = model.encode(passages, normalize_embeddings=True)


def search(question: str, k: int = 4) -> list[str]:
    scores = vectors @ model.encode(question, normalize_embeddings=True)
    return [passages[i] for i in np.argsort(-scores)[:k]]
```

## Ask the model

The prompt gives the model the passages and tells it to stay within them. Try it: fill in the
fields and open it in a chat.

:::prompt[Answer from the passages]{role="user"}
Answer the question using only the passages below. If they do not contain the answer, say so.

Question: {{ question }}

Passages:
{{ passages }}
:::

:::tip
Ask the model to quote the passage it used. Wrong answers are then easy to spot.
:::

## Check it

::::chat
:::user
When is the team offsite?
:::

:::assistant
The offsite is on 14 November in Utrecht ("Offsite: Thu 14 Nov, Utrecht", from `notes/team.md`).
:::

:::user
What is the wifi password there?
:::

:::assistant
The passages do not say.
:::
::::

:::details[Going further]
Store the vectors in a file so you embed only once, split long files into smaller passages, and
compare a few embedding models on your own questions.
:::
