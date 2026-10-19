---
title: Self-hosted app
description: The deploy guide of a made-up web app, with Docker or pip.
sidebar:
  order: 4
---

:::note[Example page]
The project, data and links on this page are made up, to show what dokk's components can do. It
does not document dokk itself.
:::

**Ledgerly** is a small bookkeeping app for teams. This guide runs it on your own server.

:::note
You need a server with 1 GB of memory, and PostgreSQL 15 or newer. SQLite works for trying it
out.
:::

## Install

::::tabs{sync="deploy"}
:::tab[Docker]
```yaml title="compose.yaml"
services:
  app:
    image: ghcr.io/example/ledgerly:3
    env_file: .env
    ports: ["8000:8000"]
    depends_on: [db]
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: change-me
    volumes: [db:/var/lib/postgresql/data]
volumes:
  db:
```

```sh
docker compose up -d
```
:::

:::tab[pip]
::install[ledgerly]{tools="pip uv"}

```sh
ledgerly migrate
ledgerly serve --host 0.0.0.0 --port 8000
```
:::
::::

## Settings

Put these in `.env`, next to `compose.yaml` or in the folder you run `ledgerly serve` from.

:::env
SECRET_KEY=                                   # A long random string; keep it secret.
DATABASE_URL=sqlite:///ledgerly.db            # postgres://user:password@db/ledgerly in production.
ALLOWED_HOSTS=localhost                       # Your domain, comma separated.
EMAIL_URL=console://                          # smtp://user:password@host:587 to send mail.
DEBUG=false                                   # Never true on a public server.
:::

:::danger
Without `SECRET_KEY` anyone can sign in as anyone. Generate one with
`python -c "import secrets; print(secrets.token_urlsafe(50))"`.
:::

## Before you go live

:::steps
1. Create the first admin: `ledgerly createadmin`.
2. Put a reverse proxy with HTTPS in front, such as Caddy or nginx.
3. Back up the database every night, and try a restore once.
4. Subscribe to the release feed to hear about security fixes.
:::

## Troubleshooting

:::details[The page shows "Bad Request (400)"]
The domain you visit is not in `ALLOWED_HOSTS`. Add it, comma separated, and restart.
:::

:::details[Emails never arrive]
`EMAIL_URL` is still `console://`, which prints mails to the log instead of sending them.
:::

:::details[Upgrading from 2.x]
Back up first, then pull the new image and run `ledgerly migrate`. 3.0 needs PostgreSQL 15.
:::

::linkbutton[Changelog]{href="changelog.md" variant="secondary"}
