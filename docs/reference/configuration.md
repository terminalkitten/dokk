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
code_light = "default"      # any Pygments style
code_dark = "github-dark"

[links]
github = "https://github.com/you/my-docs"
edit_url = "https://github.com/you/my-docs/edit/main/docs/{path}"

[search]
enabled = true              # needs the search extra
```

`{path}` in `edit_url` is the page's file path inside `content_dir`.
