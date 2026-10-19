---
title: Trace
description: The steps an agent took, one line each, with details to open.
sidebar:
  order: 7
---

`::::trace` lists the steps of an agent run, after the trace in shadcn's
[AI Elements](https://ui.shadcn.com/docs/ai-elements). Each `:::step` is a line with an icon; a
step with a body opens to show it, such as the output of a command.

````md
::::trace[Fixing the failing test]
:::step[Searched the code for parse_config]{icon="search"}
:::
:::step[Ran pytest]{icon="square-terminal" status="error"}
```text
FAILED tests/test_config.py::test_defaults - KeyError: 'title'
```
:::
:::step[Edited src/config.py]{icon="file-text"}
:::
:::step[Running pytest again]{icon="square-terminal" status="running"}
:::
::::
````

::::trace[Fixing the failing test]
:::step[Searched the code for parse_config]{icon="search"}
:::

:::step[Ran pytest]{icon="square-terminal" status="error"}
```text
FAILED tests/test_config.py::test_defaults - KeyError: 'title'
```
:::

:::step[Edited src/config.py]{icon="file-text"}
:::

:::step[Running pytest again]{icon="square-terminal" status="running"}
:::
::::

`status` is `done` (the default), `running` or `error`. Without `icon`, the status picks one: a
check, a spinner or a cross. `icon` takes any icon dokk's components use, such as `search`,
`square-terminal`, `file-text`, `wrench`, `globe`, `brain` or `code`; an unknown name fails the
build with the list.
