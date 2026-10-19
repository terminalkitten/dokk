---
title: Templates and styling
description: Override any template from your site's templates/ folder.
sidebar:
  order: 4
---

dokk renders pages with [Jinja](https://jinja.palletsprojects.com). A file in your site's `templates/`
folder replaces the built-in file with the same path.

| Template | What it renders |
|---|---|
| `base.html.jinja` | the page shell: head, sidebar, header |
| `page.html.jinja` | a content page |
| `404.html.jinja` | the not-found page (or write `docs/404.md`) |
| `partials/head.html.jinja` | extra tags at the end of `<head>`, empty by default |
| `partials/header.html.jinja` | top bar: menu button, title, search, theme toggle |
| `partials/footer.html.jinja` | site footer: `[footer] text` and the "Built with dokk" credit |
| `partials/breadcrumbs.html.jinja`, `toc.html.jinja`, `pager.html.jinja`, `page_meta.html.jinja` | page parts |
| `components/callout.html.jinja`, `tabs`, `card`, `cards`, `steps` | directive components |

For example, to replace the pager, create `templates/partials/pager.html.jinja`.

To add tags to every page's `<head>`, such as the `<meta>` tag that verifies your site in Google
Search Console, create `templates/partials/head.html.jinja`:

```jinja title="templates/partials/head.html.jinja"
<meta name="google-site-verification" content="your-token">
```

In templates, build internal URLs with `url('/some/route/')` and asset URLs with `asset('dokk.css')`,
so the base path is always right.
