---
title: Environment variables
description: A table of environment variables from .env lines, with Copy .env.
sidebar:
  order: 11
---

`:::env` turns lines written as in a `.env` file into a table: `NAME=default  # description`.
A variable without a value is required. **Copy .env** copies the lines as written, ready to paste.

```md
:::env
OPENAI_API_KEY=                 # Your API key, from the provider's dashboard.
MODEL=gpt-4o-mini               # The model to call.
MAX_TOKENS=1024                 # The longest answer, in tokens.
# Lines that start with # are skipped.
:::
```

:::env
OPENAI_API_KEY=                 # Your API key, from the provider's dashboard.
MODEL=gpt-4o-mini               # The model to call.
MAX_TOKENS=1024                 # The longest answer, in tokens.
# Lines that start with # are skipped.
:::

A line that is not `NAME=value` fails the build with its line number.
