---
title: Agent framework
description: Tools, a conversation and the trace of an agent run, for a made-up agent framework.
sidebar:
  order: 2
---

:::note[Example page]
The project, data and links on this page are made up, to show what dokk's components can do. It
does not document dokk itself.
:::

**relay** runs a model in a loop: it calls tools until the task is done. This page documents the
tools of a coding agent built with it, and shows one run.

## Project layout

:::filetree
- pyproject.toml
- **agent/**
  - main.py runs the loop
  - **tools.py** the tools below
  - prompts/
    - system.md
- tests/
:::

## Tools

Each tool is a Python function; relay sends its JSON schema to the model.

:::tool
Paths outside the repository are refused, and so are files over 1 MB.

```json
{
  "name": "read_file",
  "description": "Read a text file from the repository.",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": {"type": "string", "description": "Path relative to the repository root."},
      "start": {"type": "integer", "description": "First line to read.", "default": 1},
      "limit": {"type": ["integer", "null"], "description": "How many lines; null reads to the end."}
    },
    "required": ["path"]
  }
}
```
:::

:::tool
```json
{
  "type": "function",
  "function": {
    "name": "run_command",
    "description": "Run a shell command in the sandbox and return its output.",
    "parameters": {
      "type": "object",
      "properties": {
        "command": {"type": "string", "description": "The command, such as \"pytest -x\"."},
        "timeout": {"type": "integer", "description": "Seconds before it is stopped.", "default": 120},
        "env": {"type": "array", "items": {"type": "string"}, "description": "Extra NAME=value pairs."}
      },
      "required": ["command"]
    }
  }
}
```
:::

:::tip
The second tool is written in OpenAI's format and the first in Anthropic's: `:::tool` reads both.
:::

## The system prompt

:::prompt[Coding agent]{role="system" open="false"}
You fix failing tests in a Python repository.

1. Run the tests first and read the failure.
2. Read only the files you need.
3. Make the smallest change that fixes it, then run the tests again.
:::

## A run

The user asks for a fix; the agent answers after five steps.

::::chat
:::user
`test_defaults` fails since yesterday. Can you fix it?
:::

:::assistant[relay]{icon="claude"}
Fixed: `load_config` no longer drops the `title` key when the file has no `[site]` table. All
42 tests pass.
:::
::::

What happened in between:

::::trace[Fixing test_defaults]
:::step[Ran pytest -x]{icon="square-terminal" status="error"}
```text
FAILED tests/test_config.py::test_defaults - KeyError: 'title'
```
:::

:::step[Searched the code for load_config]{icon="search"}
:::

:::step[Read src/config.py]{icon="file-text"}
:::

:::step[Edited src/config.py]{icon="wrench"}
```diff
-    site = data["site"]
+    site = data.get("site", {})
```
:::

:::step[Ran pytest]{icon="square-terminal"}
```text
42 passed in 0.81s
```
:::
::::

:::details[Why a trace?]
Readers trust an agent more when they can see what it did. A trace is also the quickest way to
document a run in a bug report.
:::
