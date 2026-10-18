---
title: Deploy to GitHub Pages
description: Publish with the workflow dokk init creates.
sidebar:
  order: 5
---

:::steps
1. Set `site_url` in `dokk.toml` to your Pages URL, for example
   `https://you.github.io/my-docs/`. dokk derives the base path (`/my-docs`) from it.
2. Push the repository, including `.github/workflows/docs.yml` from `dokk init`.
3. In the repository settings, under **Pages**, set the source to **GitHub Actions**.
:::

On every push to `main`, the workflow runs `dokk check`, builds the site and deploys it.

The build also writes `.nojekyll`, `404.html`, `sitemap.xml` and `robots.txt`. A `CNAME` file in
`public/` sets a custom domain.
