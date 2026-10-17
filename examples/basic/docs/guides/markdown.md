---
title: Markdown features
sidebar:
  order: 1
---

Everything dokk renders at build time, with "smart quotes" -- and no client-side parser.

## Code

Python:

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

JavaScript:

```js
const greet = (name) => `Hello, ${name}!`;
```

Inline `code` and an unknown language:

```nosuchlang
plain text
```

## Tables and lists

| Feature | Status |
|---|---|
| Tables | ~~planned~~ done |
| Footnotes | done[^1] |

- [x] Task lists
- [ ] Directives (Phase 3)

Term
: Definition lists work too.

### Links and images

Read [installation](../getting-started/install.md#requirements), [the home page](../index.md),
an [absolute link](/getting-started/) and [an external one](https://example.com).

![Diagram](img/diagram.png)

## Sidebar

A heading named "Sidebar" must not clash with the layout's sidebar id.

[^1]: Footnotes render at the bottom of the page.
