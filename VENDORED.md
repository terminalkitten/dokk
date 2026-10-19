# Vendored files

Update with the scripts below (Python standard library only, no Node); they overwrite files in
place and print the values to record here.

## Basecoat

- Package: `basecoat-css@1.0.2` (MIT, see `src/dokk/static/vendor/basecoat/LICENSE`)
- Tarball: https://registry.npmjs.org/basecoat-css/-/basecoat-css-1.0.2.tgz
- Integrity: `sha512-C6I5rr7HziIAoBYNGPO5U6HaU/6FuF3iVp++IgoEqqJ836is3XoRty6l1ibXqxnoIRZNnOAYDMX8QxVC+58zhw==`
- Updated with: `python scripts/vendor_basecoat.py 1.0.2` (checks the tarball against the integrity)

| Source in package | Destination |
|---|---|
| `dist/basecoat-{vega,nova,maia,lyra,mira,luma,sera,rhea}.cdn.min.css` | `src/dokk/static/vendor/basecoat/` |
| `dist/js/all.min.js` | `src/dokk/static/vendor/basecoat/` |
| `LICENSE.md` (as `LICENSE`) | `src/dokk/static/vendor/basecoat/` |
| `templates/jinja/*.html.jinja` | `src/dokk/templates/basecoat/` |

## shadcn/ui color themes

- Source: `apps/v4/registry/themes.ts` in https://github.com/shadcn-ui/ui (MIT, see `src/dokk/data/SHADCN-LICENSE`)
- Commit: `d2fba50ee5b9113008b5bb908563527b7efd2f27` (2026-10-16)
- Updated with: `python scripts/vendor_shadcn_themes.py [commit]`
- Converted to `src/dokk/data/shadcn-themes.json`: 7 base colors, 17 accent colors, light and dark

## Icons and logos

Inline SVG pasted into templates, as Basecoat recommends; nothing is downloaded at build time.

- `src/dokk/templates/partials/icons.html.jinja` and the component templates: [Lucide](https://lucide.dev)
  `lucide-static@1.59.0` (ISC, see `src/dokk/data/LUCIDE-LICENSE`)
- `src/dokk/templates/partials/logos.html.jinja`: vendor logos from [Simple Icons](https://simpleicons.org)
  `simple-icons@16.35.0` (CC0, see `src/dokk/data/SIMPLE-ICONS-LICENSE`), except `openai` from
  [LobeHub Icons](https://lobehub.com/icons) `@lobehub/icons-static-svg@1.95.1` (MIT, see
  `src/dokk/data/LOBEHUB-ICONS-LICENSE`). The logos are trademarks of their owners.
- To add one: copy the paths inside the icon's `<svg>` from
  `https://cdn.jsdelivr.net/npm/<package>/icons/<name>.svg` into the dict (24×24 viewBox).
