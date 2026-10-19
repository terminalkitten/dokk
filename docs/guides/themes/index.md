---
title: Themes
description: Style packs for shape and density, base and accent colors, code highlighting.
sidebar:
  order: 3
---

A theme is three choices in `dokk.toml`, the way [Basecoat](https://basecoatui.com/customization/)
themes: a **style** pack for shape and density, a **base** color for every surface and text color,
and an optional accent **color** on top.

```toml title="dokk.toml"
[theme]
style = "rhea"
base = "zinc"
color = "pink"
```

Only the chosen style pack is copied into your site.

## Styles

A style pack sets the size of controls, corner radius and spacing. Measured on a default button,
input and card:

| Style            | Controls | Corners                  | Feel                        |
| ---------------- | -------- | ------------------------ | --------------------------- |
| `vega` (default) | 36px     | 8px inputs, 14px cards   | the classic shadcn/ui look  |
| `nova`           | 32px     | 10px inputs, 14px cards  | vega, tighter               |
| `maia`           | 36px     | pill inputs, 16px cards  | soft and rounded            |
| `lyra`           | 32px     | square                   | boxy and sharp              |
| `mira`           | 28px     | 8px inputs, 10px cards   | the densest, for busy pages |
| `luma`           | 36px     | 24px inputs, 32px cards  | the roundest, airy          |
| `sera`           | 40px     | square, uppercase badges | large and roomy             |
| `rhea`           | 32px     | 16px inputs, 24px cards  | compact but rounded         |

## Base colors

The base sets every token: backgrounds, text, borders, muted surfaces. Each is tuned for light and
dark mode. Shown: background, foreground, primary, muted and border.

| Base                | Light                                                                                                                                                              | Dark                                                                                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `neutral` (default) | :swatch[oklch(1 0 0)] :swatch[oklch(0.145 0 0)] :swatch[oklch(0.205 0 0)] :swatch[oklch(0.97 0 0)] :swatch[oklch(0.922 0 0)]                                       | :swatch[oklch(0.145 0 0)] :swatch[oklch(0.985 0 0)] :swatch[oklch(0.922 0 0)] :swatch[oklch(0.269 0 0)] :swatch[oklch(1 0 0 / 10%)]                                     |
| `stone`             | :swatch[oklch(1 0 0)] :swatch[oklch(0.147 0.004 49.25)] :swatch[oklch(0.216 0.006 56.043)] :swatch[oklch(0.97 0.001 106.424)] :swatch[oklch(0.923 0.003 48.717)]   | :swatch[oklch(0.147 0.004 49.25)] :swatch[oklch(0.985 0.001 106.423)] :swatch[oklch(0.923 0.003 48.717)] :swatch[oklch(0.268 0.007 34.298)] :swatch[oklch(1 0 0 / 10%)] |
| `zinc`              | :swatch[oklch(1 0 0)] :swatch[oklch(0.141 0.005 285.823)] :swatch[oklch(0.21 0.006 285.885)] :swatch[oklch(0.967 0.001 286.375)] :swatch[oklch(0.92 0.004 286.32)] | :swatch[oklch(0.141 0.005 285.823)] :swatch[oklch(0.985 0 0)] :swatch[oklch(0.92 0.004 286.32)] :swatch[oklch(0.274 0.006 286.033)] :swatch[oklch(1 0 0 / 10%)]         |
| `mauve`             | :swatch[oklch(1 0 0)] :swatch[oklch(0.145 0.008 326)] :swatch[oklch(0.212 0.019 322.12)] :swatch[oklch(0.96 0.003 325.6)] :swatch[oklch(0.922 0.005 325.62)]       | :swatch[oklch(0.145 0.008 326)] :swatch[oklch(0.985 0 0)] :swatch[oklch(0.922 0.005 325.62)] :swatch[oklch(0.263 0.024 320.12)] :swatch[oklch(1 0 0 / 10%)]             |
| `olive`             | :swatch[oklch(1 0 0)] :swatch[oklch(0.153 0.006 107.1)] :swatch[oklch(0.228 0.013 107.4)] :swatch[oklch(0.966 0.005 106.5)] :swatch[oklch(0.93 0.007 106.5)]       | :swatch[oklch(0.153 0.006 107.1)] :swatch[oklch(0.988 0.003 106.5)] :swatch[oklch(0.93 0.007 106.5)] :swatch[oklch(0.286 0.016 107.4)] :swatch[oklch(1 0 0 / 10%)]      |
| `mist`              | :swatch[oklch(1 0 0)] :swatch[oklch(0.148 0.004 228.8)] :swatch[oklch(0.218 0.008 223.9)] :swatch[oklch(0.963 0.002 197.1)] :swatch[oklch(0.925 0.005 214.3)]      | :swatch[oklch(0.148 0.004 228.8)] :swatch[oklch(0.987 0.002 197.1)] :swatch[oklch(0.925 0.005 214.3)] :swatch[oklch(0.275 0.011 216.9)] :swatch[oklch(1 0 0 / 10%)]     |
| `taupe`             | :swatch[oklch(1 0 0)] :swatch[oklch(0.147 0.004 49.3)] :swatch[oklch(0.214 0.009 43.1)] :swatch[oklch(0.96 0.002 17.2)] :swatch[oklch(0.922 0.005 34.3)]           | :swatch[oklch(0.147 0.004 49.3)] :swatch[oklch(0.986 0.002 67.8)] :swatch[oklch(0.922 0.005 34.3)] :swatch[oklch(0.268 0.011 36.5)] :swatch[oklch(1 0 0 / 10%)]         |

## Accent colors

`color` adds an accent on top of the base: primary, secondary, the sidebar accent and five chart
colors. The chart colors are the same in light and dark mode. Leave `color` out to keep the base's
own primary.

| Color     | Primary, light                      | Primary, dark                       | Charts                                                                                                                                                                              | Code (light / dark)                  |
| --------- | ----------------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| `amber`   | :swatch[oklch(0.555 0.163 48.998)]  | :swatch[oklch(0.473 0.137 46.201)]  | :swatch[oklch(0.879 0.169 91.605)] :swatch[oklch(0.769 0.188 70.08)] :swatch[oklch(0.666 0.179 58.318)] :swatch[oklch(0.555 0.163 48.998)] :swatch[oklch(0.473 0.137 46.201)]       | `gruvbox-light` / `gruvbox-dark`     |
| `blue`    | :swatch[oklch(0.488 0.243 264.376)] | :swatch[oklch(0.424 0.199 265.638)] | :swatch[oklch(0.809 0.105 251.813)] :swatch[oklch(0.623 0.214 259.815)] :swatch[oklch(0.546 0.245 262.881)] :swatch[oklch(0.488 0.243 264.376)] :swatch[oklch(0.424 0.199 265.638)] | `vs` / `one-dark`                    |
| `cyan`    | :swatch[oklch(0.52 0.105 223.128)]  | :swatch[oklch(0.45 0.085 224.283)]  | :swatch[oklch(0.865 0.127 207.078)] :swatch[oklch(0.715 0.143 215.221)] :swatch[oklch(0.609 0.126 221.723)] :swatch[oklch(0.52 0.105 223.128)] :swatch[oklch(0.45 0.085 224.283)]   | `solarized-light` / `solarized-dark` |
| `emerald` | :swatch[oklch(0.508 0.118 165.612)] | :swatch[oklch(0.432 0.095 166.913)] | :swatch[oklch(0.845 0.143 164.978)] :swatch[oklch(0.696 0.17 162.48)] :swatch[oklch(0.596 0.145 163.225)] :swatch[oklch(0.508 0.118 165.612)] :swatch[oklch(0.432 0.095 166.913)]   | `friendly` / `nord`                  |
| `fuchsia` | :swatch[oklch(0.518 0.253 323.949)] | :swatch[oklch(0.452 0.211 324.591)] | :swatch[oklch(0.833 0.145 321.434)] :swatch[oklch(0.667 0.295 322.15)] :swatch[oklch(0.591 0.293 322.896)] :swatch[oklch(0.518 0.253 323.949)] :swatch[oklch(0.452 0.211 324.591)]  | `lovelace` / `dracula`               |
| `green`   | :swatch[oklch(0.527 0.154 150.069)] | :swatch[oklch(0.448 0.119 151.328)] | :swatch[oklch(0.871 0.15 154.449)] :swatch[oklch(0.723 0.219 149.579)] :swatch[oklch(0.627 0.194 149.214)] :swatch[oklch(0.527 0.154 150.069)] :swatch[oklch(0.448 0.119 151.328)]  | `friendly` / `nord`                  |
| `indigo`  | :swatch[oklch(0.457 0.24 277.023)]  | :swatch[oklch(0.398 0.195 277.366)] | :swatch[oklch(0.785 0.115 274.713)] :swatch[oklch(0.585 0.233 277.117)] :swatch[oklch(0.511 0.262 276.966)] :swatch[oklch(0.457 0.24 277.023)] :swatch[oklch(0.398 0.195 277.366)]  | `vs` / `one-dark`                    |
| `lime`    | :swatch[oklch(0.841 0.238 128.85)]  | :swatch[oklch(0.768 0.233 130.85)]  | :swatch[oklch(0.897 0.196 126.665)] :swatch[oklch(0.768 0.233 130.85)] :swatch[oklch(0.648 0.2 131.684)] :swatch[oklch(0.532 0.157 131.589)] :swatch[oklch(0.453 0.124 130.933)]    | `friendly` / `nord`                  |
| `orange`  | :swatch[oklch(0.553 0.195 38.402)]  | :swatch[oklch(0.47 0.157 37.304)]   | :swatch[oklch(0.837 0.128 66.29)] :swatch[oklch(0.705 0.213 47.604)] :swatch[oklch(0.646 0.222 41.116)] :swatch[oklch(0.553 0.195 38.402)] :swatch[oklch(0.47 0.157 37.304)]        | `gruvbox-light` / `gruvbox-dark`     |
| `pink`    | :swatch[oklch(0.525 0.223 3.958)]   | :swatch[oklch(0.459 0.187 3.815)]   | :swatch[oklch(0.823 0.12 346.018)] :swatch[oklch(0.656 0.241 354.308)] :swatch[oklch(0.592 0.249 0.584)] :swatch[oklch(0.525 0.223 3.958)] :swatch[oklch(0.459 0.187 3.815)]        | `pastie` / `monokai`                 |
| `purple`  | :swatch[oklch(0.496 0.265 301.924)] | :swatch[oklch(0.438 0.218 303.724)] | :swatch[oklch(0.827 0.119 306.383)] :swatch[oklch(0.627 0.265 303.9)] :swatch[oklch(0.558 0.288 302.321)] :swatch[oklch(0.496 0.265 301.924)] :swatch[oklch(0.438 0.218 303.724)]   | `lovelace` / `dracula`               |
| `red`     | :swatch[oklch(0.505 0.213 27.518)]  | :swatch[oklch(0.444 0.177 26.899)]  | :swatch[oklch(0.808 0.114 19.571)] :swatch[oklch(0.637 0.237 25.331)] :swatch[oklch(0.577 0.245 27.325)] :swatch[oklch(0.505 0.213 27.518)] :swatch[oklch(0.444 0.177 26.899)]      | `pastie` / `monokai`                 |
| `rose`    | :swatch[oklch(0.514 0.222 16.935)]  | :swatch[oklch(0.455 0.188 13.697)]  | :swatch[oklch(0.81 0.117 11.638)] :swatch[oklch(0.645 0.246 16.439)] :swatch[oklch(0.586 0.253 17.585)] :swatch[oklch(0.514 0.222 16.935)] :swatch[oklch(0.455 0.188 13.697)]       | `pastie` / `monokai`                 |
| `sky`     | :swatch[oklch(0.5 0.134 242.749)]   | :swatch[oklch(0.443 0.11 240.79)]   | :swatch[oklch(0.828 0.111 230.318)] :swatch[oklch(0.685 0.169 237.323)] :swatch[oklch(0.588 0.158 241.966)] :swatch[oklch(0.5 0.134 242.749)] :swatch[oklch(0.443 0.11 240.79)]     | `vs` / `one-dark`                    |
| `teal`    | :swatch[oklch(0.511 0.096 186.391)] | :swatch[oklch(0.437 0.078 188.216)] | :swatch[oklch(0.855 0.138 181.071)] :swatch[oklch(0.704 0.14 182.503)] :swatch[oklch(0.6 0.118 184.704)] :swatch[oklch(0.511 0.096 186.391)] :swatch[oklch(0.437 0.078 188.216)]    | `solarized-light` / `solarized-dark` |
| `violet`  | :swatch[oklch(0.491 0.27 292.581)]  | :swatch[oklch(0.432 0.232 292.759)] | :swatch[oklch(0.811 0.111 293.571)] :swatch[oklch(0.606 0.25 292.717)] :swatch[oklch(0.541 0.281 293.009)] :swatch[oklch(0.491 0.27 292.581)] :swatch[oklch(0.432 0.232 292.759)]   | `lovelace` / `dracula`               |
| `yellow`  | :swatch[oklch(0.852 0.199 91.936)]  | :swatch[oklch(0.795 0.184 86.047)]  | :swatch[oklch(0.905 0.182 98.111)] :swatch[oklch(0.795 0.184 86.047)] :swatch[oklch(0.681 0.162 75.834)] :swatch[oklch(0.554 0.135 66.442)] :swatch[oklch(0.476 0.114 61.907)]      | `gruvbox-light` / `gruvbox-dark`     |

## Code highlighting

The accent also picks the [Pygments](https://pygments.org/styles/) styles for code blocks (last
column above). Without an accent, code uses `default` and `github-dark`. Override either one:

```toml title="dokk.toml"
[theme]
color = "pink"
code_light = "friendly"   # any Pygments style
code_dark = "nord"
```

## Fine-tuning

To change single colors, override `templates/files/theme.css.jinja` in your site. It receives
`base`, `color` and `vars`, with the final tokens in `vars.light` and `vars.dark`. See
[Templates and styling](../templates.md).

Colors are from [shadcn/ui](https://ui.shadcn.com/themes) (MIT), as vendored in dokk.
