---
title: Install
description: pip, uv and poetry commands for a Python package, as synced tabs.
sidebar:
  order: 10
---

`::install[package]` writes the install command for pip, uv and poetry as tabs. Every install
block on the site switches together, and the reader's choice is remembered.

```md
::install[dokk[search]]
```

::install[dokk[search]]

For a development dependency, add `dev="true"`: `uv add --dev` and `poetry add --group dev`;
pip has no such thing and stays the same.

```md
::install[pytest]{dev="true"}
```

::install[pytest]{dev="true"}

`tools` picks the installers and their order, such as `tools="uv pip"`.
