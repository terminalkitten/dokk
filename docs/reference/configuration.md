---
title: Configuration
description: Every key in dokk.toml.
sidebar:
  order: 2
---

Only `title` is required.

```toml
title = "My docs"
description = "Shown in search results"
site_url = "https://you.github.io/my-docs/"  # canonical URLs, sitemap, base path
content_dir = "docs"
out_dir = ".dokk/build"
lang = "en"

[theme]
style = "vega"              # Basecoat style pack, see Themes
base = "neutral"            # shadcn base color
color = "blue"              # shadcn accent color (optional)
code_light = "vs"           # any Pygments style; defaults follow the color
code_dark = "one-dark"

[links]
github = "https://github.com/you/my-docs"
edit_url = "https://github.com/you/my-docs/edit/main/docs/{path}"

[search]
enabled = true              # needs the search extra

[llms]
enabled = true              # writes llms.txt and llms-full.txt for AI tools

[footer]
text = "© 2026 My company"  # an optional line at the bottom of every page
credit = true               # "Built with dokk"; false hides it
```

`{path}` in `edit_url` is the page's file path inside `content_dir`.

The footer shows "Built with dokk" with a link unless `credit = false`. For a different footer,
override `templates/partials/footer.html.jinja`.

Unknown keys are an error, so a typo like `enable = true` fails the build instead of being
ignored. `[links]` is the exception: custom templates can read any key from it.

## Sidebar

Without `[[sidebar]]` the menu follows your folders. Add `[[sidebar]]` tables to choose the
order, mix generated folders with hand-picked pages, and add external links:

```toml
[[sidebar]]
label = "Start"
items = ["index.md", { page = "intro.md", label = "Introduction" }]

[[sidebar]]
autogenerate = "guides"          # the folder, generated as without config

[[sidebar]]
label = "Links"
items = [
  { label = "GitHub", link = "https://github.com/you/my-docs" },
  { label = "More", items = ["extra/a.md", "extra/b.md"] },   # a submenu
]
```

Each top-level table is a group. Pages are paths inside `content_dir`. Pages you leave out are
still built; `dokk check` warns about them unless they have `sidebar.hidden: true`.

## llms.txt

With `[llms] enabled = true`, the build writes [`llms.txt`](https://llmstxt.org): a Markdown
index of your pages grouped like the sidebar, with descriptions. `llms-full.txt` holds every
page's Markdown source in one file. Pages with `noindex: true` are left out.

## Theme

`[theme]` picks a Basecoat style pack, a base color, an accent color and code highlighting. See
[Themes](../guides/themes/index.md) for every option, with color swatches.
