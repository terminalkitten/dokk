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
out_dir = "dist"
lang = "en"

[theme]
style = "vega"              # Basecoat style pack, see below
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
```

`{path}` in `edit_url` is the page's file path inside `content_dir`.

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

## Style and color

dokk themes the way [Basecoat](https://basecoatui.com/customization/) does: one style pack,
then shadcn/ui color tokens on top.

- `style` picks the Basecoat style pack: shape, density and radius. One of `vega` (default),
  `nova`, `maia`, `lyra`, `mira`, `luma`, `sera` or `rhea`.
- `base` picks a shadcn base color: every token, tuned for light and dark. One of `neutral`
  (default), `stone`, `zinc`, `mauve`, `olive`, `mist` or `taupe`.
- `color` adds a shadcn accent on top: primary, secondary, sidebar accent and five chart colors,
  each tuned for light and dark. One of `amber`, `blue`, `cyan`, `emerald`, `fuchsia`, `green`,
  `indigo`, `lime`, `orange`, `pink`, `purple`, `red`, `rose`, `sky`, `teal`, `violet` or `yellow`.

```toml
[theme]
style = "rhea"
base = "zinc"
color = "pink"
```

The accent also picks matching code highlighting (pink uses `pastie` and `monokai`);
`code_light` and `code_dark` override it. Only the chosen style pack is copied into your site.

To fine-tune colors, override `templates/files/theme.css.jinja` in your site. It receives
`base`, `color` and `vars` (`vars.light` and `vars.dark`).
