---
title: Custom components
description: Register your own directive by adding a template.
sidebar:
  order: 10
---

Add a template to your site's `templates/components/` folder and its file name becomes a
directive. `templates/components/note-box.html.jinja` is used as `:::note-box` or `::note-box`.

:::filetree
- dokk.toml
- docs/
- templates/
  - components/
    - **note-box.html.jinja** registers `:::note-box`
:::

The template gets the same values as the built-in components:

`directive.title`
: The text in `[...]`.

`directive.attrs`
: The `{key="value"}` attributes. Relative `href` and `src` values are already rewritten to site
  URLs, and missing targets are reported as broken links.

`body`
: The rendered Markdown inside a `:::` block; empty for a one-line `::` directive.

`id`
: An id that is unique on the page, such as `dk-note-box-1`. Use it for scripts and labels.

Templates also have `url()`, `asset()` and `site`. A template that reads a missing attribute fails
the build, so use `directive.attrs.get("key", "default")` for optional ones.

```jinja title="templates/components/note-box.html.jinja"
<aside class="card" id="{{ id }}">
  <header><h2>{{ directive.title or "Note" }}</h2></header>
  <section>{{ body }}</section>
</aside>
```

```md
:::note-box[Heads up]
Any **Markdown** here.
:::
```

A template with the name of a built-in component, such as `tabs`, replaces it. An unknown
directive name still fails the build, with the file and line.

:::tip
The [Theme showcase](../themes/showcase.md) is a custom component of these docs: a template with its
own `<style>` and `<script>`. See `templates/components/themepicker.html.jinja` in the repository.
:::
