---
title: Components
sidebar:
  order: 2
---

Every component on one page, as a fixture for builds and browser tests.

## Callouts

:::note
Widgets ship fully assembled, mostly.
:::

:::tip[Pro tip]
Callouts can hold **Markdown**, `code` and [links](../getting-started/install.md).
:::

:::caution
Do not overtighten the sprocket.
:::

:::danger[Do not <script>]
Titles are escaped.
:::

## Tabs

::::tabs{sync="pkg"}
:::tab[npm]
```sh
npm install acme-widgets
```
:::
:::tab[yarn]
```sh
yarn add acme-widgets
```
:::
::::

A second tab set gets its own id. Nesting needs more colons on each outer fence:

:::::tabs
::::tab[One]
First panel.
::::
::::tab[Two]
:::note
Directives nest inside tabs.
:::
::::
:::::

## Synced tabs

Same `sync` key as the install tabs above: they switch together.

::::tabs{sync="pkg"}
:::tab[npm]
```sh
npm run build
```
:::
:::tab[yarn]
```sh
yarn build
```
:::
::::

## Cards

::::cards
:::card[Quick start]{href="../getting-started/index.md"}
Unbox your first widget.
:::
:::card[Writing]{href="/guides/writing/"}
Pages, links and images.
:::
:::card[No link]
A plain card.
:::
::::

## Steps

:::steps
1. Unbox the widget.
2. Tighten the bolts.
3. Press the big red button.
:::

## Details

:::details[What is inside the box?]
One widget, two bolts and a slightly crumpled manual.
:::

## Badges

The sprocket :badge[New] spins :badge[Beta]{variant="secondary"} and the anvil
:badge[Heavy]{variant="outline"} is :badge[Deprecated]{variant="danger"}.

## File tree

:::filetree
- widget.toml
- **src**
  - sprocket.py the main part
  - gears/
  - …
- `READ ME.md`
:::

## Link buttons

::linkbutton[Get started]{href="../getting-started/index.md"}
::linkbutton[Acme on GitHub]{href="https://github.com/acme/widgets" variant="secondary"}
::linkbutton[Order spare parts]{href="https://example.com" variant="minimal"}

## Code

```python title="sprocket.py" {2}
def spin(speed: int) -> str:
    return "whirr" * speed
```
