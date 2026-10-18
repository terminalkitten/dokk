---
title: Markdown features
sidebar:
  order: 1
---

Everything a widget manual needs, with "smart quotes" -- and no client-side parser.

## Code

Python:

```python
def assemble(widget: str) -> str:
    return f"Assembled {widget}!"
```

JavaScript:

```js
const assemble = (widget) => `Assembled ${widget}!`;
```

Inline `code` and an unknown language:

```nosuchlang
plain text
```

## Tables and lists

| Widget | Status |
|---|---|
| Sprocket | ~~planned~~ shipped |
| Anvil | heavy[^1] |

- [x] Tighten bolts
- [ ] Paint it beige

Gizmo
: A widget that does one thing, loudly.

### Links and images

Read [installation](../getting-started/install.md#requirements), [the home page](../index.md),
an [absolute link](/getting-started/) and [an external one](https://example.com).

![Diagram](img/diagram.png)

## Sidebar

A heading named "Sidebar" must not clash with the layout's sidebar id.

[^1]: About 50 kg. Do not drop on feet.
