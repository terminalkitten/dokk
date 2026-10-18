---
title: Writing pages
description: Folders, front matter, the sidebar, links and images.
sidebar:
  order: 1
---

## Folders become the menu

Every `.md` file under `docs/` is a page. Folders become sidebar groups, and nested folders become
collapsible submenus.

| Source file | URL |
|---|---|
| `docs/index.md` | `/` |
| `docs/guides/index.md` | `/guides/` |
| `docs/guides/intro.md` | `/guides/intro/` |
| `docs/Getting Started.md` | `/getting-started/` |

A folder's `index.md` is the first item inside it. Two files that map to the same URL fail the build.

## Front matter

```yaml
---
title: Installation            # page title; else the first "# heading", else the file name
description: How to install.   # meta description; else the first paragraph
draft: true                    # skipped in builds, shown by dokk serve and --drafts
noindex: true                  # kept out of sitemap.xml and search engines
sidebar:
  label: Install               # menu text instead of the title
  order: 1                     # lower comes first; unordered pages follow by file name
  hidden: true                 # built, but not in the menu
  badge: New                   # or {text: New, variant: secondary}
---
```

A folder takes its menu title and order from its `index.md`. A folder without one sorts after
ordered entries and uses its name, title-cased.

## Links and images

Link to other pages by their file, relative to the current one. dokk turns them into the right URL,
including the base path on GitHub Pages:

```md
See [installation](../getting-started/index.md#install).
![Diagram](img/diagram.png)
```

Files next to your Markdown (images, PDFs, …) are copied to the site. Files in `public/` are copied to
the site root, for example `favicon.svg` or `CNAME`.

:::caution
Links written as raw HTML (`<a href>`, `<img src>`) are not rewritten. Use Markdown syntax.
:::

## Markdown features

Tables, ~~strikethrough~~, footnotes[^1], task lists, definition lists, heading anchors and
attributes like `{#id .class}` all work. Code blocks are highlighted at build time:

```python
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

Add a title and highlight lines after the language:

````md
```python title="hello.py" {2}
def hello(name: str) -> str:
    return f"Hello, {name}!"
```
````

```python title="hello.py" {2}
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

[^1]: Like this one.
