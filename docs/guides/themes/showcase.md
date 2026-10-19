---
title: Theme showcase
description: Try every Basecoat style pack and shadcn/ui color on these docs, live.
sidebar:
  label: Showcase
  order: 1
---

Pick a style, base color and accent color, and this page restyles itself. Use the light/dark
toggle in the header to see both modes, then copy the `[theme]` table into your `dokk.toml`.

::themepicker

## Palette

The colors of the current theme, live:

| Token | Swatch | Token | Swatch |
|---|---|---|---|
| `background` | :swatch[var(--background)] | `foreground` | :swatch[var(--foreground)] |
| `primary` | :swatch[var(--primary)] | `primary-foreground` | :swatch[var(--primary-foreground)] |
| `secondary` | :swatch[var(--secondary)] | `muted` | :swatch[var(--muted)] |
| `accent` | :swatch[var(--accent)] | `border` | :swatch[var(--border)] |
| `destructive` | :swatch[var(--destructive)] | `ring` | :swatch[var(--ring)] |

Charts: :swatch[var(--chart-1)] :swatch[var(--chart-2)] :swatch[var(--chart-3)]
:swatch[var(--chart-4)] :swatch[var(--chart-5)]

## Buttons and forms

Style packs differ most here: height, corners, padding and weight.

<div class="dk-showcase-row">
  <button type="button" class="btn">Primary</button>
  <button type="button" class="btn" data-variant="secondary">Secondary</button>
  <button type="button" class="btn" data-variant="outline">Outline</button>
  <button type="button" class="btn" data-variant="ghost">Ghost</button>
  <button type="button" class="btn" data-variant="destructive">Destructive</button>
  <button type="button" class="btn" data-variant="link">Link</button>
</div>

<div class="dk-showcase-row">
  <button type="button" class="btn" data-size="sm">Small</button>
  <button type="button" class="btn" data-size="lg">Large</button>
  <button type="button" class="btn" disabled>Disabled</button>
  <span class="badge">Badge</span>
  <span class="badge" data-variant="secondary">Secondary</span>
  <span class="badge" data-variant="outline">Outline</span>
  <span class="badge" data-variant="destructive">Destructive</span>
</div>

<form class="dk-showcase-form" onsubmit="return false">
  <div class="field">
    <label class="label" for="showcase-email">Email</label>
    <input class="input" id="showcase-email" type="email" placeholder="you@example.com">
  </div>
  <div class="field">
    <label class="label" for="showcase-plan">Plan</label>
    <select id="showcase-plan"><option>Hobby</option><option>Team</option></select>
  </div>
  <div class="field dk-showcase-wide">
    <label class="label" for="showcase-message">Message</label>
    <textarea class="textarea" id="showcase-message" rows="2" placeholder="Hello"></textarea>
  </div>
  <label class="label"><input type="checkbox" class="input" checked> Remember me</label>
  <label class="label"><input type="checkbox" role="switch" class="input" checked> Notifications</label>
  <label class="label"><input type="radio" class="input" name="showcase-r" checked> Monthly</label>
  <label class="label"><input type="radio" class="input" name="showcase-r"> Yearly</label>
</form>

## Components

:::note
A note with a [link](index.md) and `inline code`.
:::

:::tip[Custom title]
Tips, cautions and warnings use the same alert, in their own colors.
:::

:::caution
Careful with this one.
:::

:::danger
And this one breaks things.
:::

::::tabs{sync="pkg"}
:::tab[pip]
```sh
pip install "dokk[serve,search]"
```
:::
:::tab[uv]
```sh
uv pip install "dokk[serve,search]"
```
:::
::::

::::cards
:::card[Writing pages]{href="../writing.md"}
Folders, front matter, links and images.
:::
:::card[Components]{href="../components/index.md"}
Everything on this page, documented.
:::
::::

:::steps
1. Pick a style, base and color above.
2. Copy the `[theme]` table.
3. Paste it into `dokk.toml` and run `dokk build`.
:::

:::details[A collapsible block]
Hidden until opened. Press :kbd[Ctrl+K] to search, or :kbd[/].
:::

:::filetree
- dokk.toml
- **docs/**
  - index.md the home page
  - guides/
- public/
:::

::linkbutton[Get started]{href="../../getting-started/index.md"}
::linkbutton[Themes]{href="index.md" variant="secondary"}
::linkbutton[Basecoat]{href="https://basecoatui.com" variant="minimal"}

Badges inline: :badge[New] :badge[Beta]{variant="secondary"} :badge[Draft]{variant="outline"}
:badge[Removed]{variant="danger"}

::image[The Writing pages guide]{src="../components/img/example.jpg" caption="Click to enlarge."}

## Text

Body text with **bold**, *italic*, ~~struck~~, a [link](index.md) and `inline code`. A
footnote, too.[^1]

> A quote, set apart from the text around it.

- A list item
  - nested
- [x] a done task
- [ ] an open task

| Setting | Default | What it does |
|---|---|---|
| `style` | `vega` | shape and density |
| `base` | `neutral` | every surface and text color |
| `color` | none | the accent on top |

```python title="hello.py" {2}
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

[^1]: Footnotes collect at the end of the page.

## About this page

Code blocks keep these docs' own highlighting; in your site it follows the accent color. See
[Themes](index.md) for what each setting does.

:::note[Only for these docs]
A normal dokk site ships just the style pack named in its `dokk.toml`. These docs also publish
the other seven, so this picker can switch between them.
:::

:::note[A custom component]
The picker is not built into dokk: it is a [custom component](../components/custom.md) of these
docs, a template in `templates/components/themepicker.html.jinja`.
:::
