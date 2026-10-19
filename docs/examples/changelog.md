---
title: Changelog
description: Release notes of a made-up project, newest first.
sidebar:
  order: 5
---

Every release of Ledgerly, newest first. We follow [semantic versioning](https://semver.org):
upgrade within a major version without changes. :badge[Example]{variant="secondary"}

## 3.1.0 :badge[Latest] { #v3-1-0 }

*Released 12 October 2026*

- :badge[New] Export any report as CSV or PDF.
- :badge[New] Keyboard shortcuts: :kbd[N] for a new entry, :kbd[/] to search.
- :badge[Fixed]{variant="secondary"} Totals in foreign currencies were rounded twice.
- :badge[Fixed]{variant="secondary"} The date picker started on Sunday in every locale.

## 3.0.0 { #v3-0-0 }

*Released 1 September 2026*

:::caution[Breaking changes]
- PostgreSQL 15 or newer is required.
- The `/api/v1` endpoints are gone; use `/api/v2`.
:::

- :badge[New] Teams: invite people and share ledgers.
- :badge[New] Dark mode.
- :badge[Removed]{variant="danger"} The XML export, replaced by CSV.

:::details[Upgrade guide]
1. Back up the database.
2. Upgrade PostgreSQL to 15 or newer.
3. Pull the new version and run `ledgerly migrate`.
:::

## 2.4.2 { #v2-4-2 }

*Released 3 July 2026*

- :badge[Security]{variant="danger"} Sessions now end when the password changes. Upgrade soon.

## Older releases

See the [releases on GitHub](https://github.com/example/ledgerly/releases) for 2.4.1 and earlier.
