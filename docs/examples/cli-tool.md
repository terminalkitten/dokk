---
title: Command-line tool
description: The docs of a made-up command-line tool, with install, commands, options and config.
sidebar:
  order: 2
---

:::note[Example page]
The project, data and links on this page are made up, to show what dokk's components can do. It
does not document dokk itself.
:::

**tidy** sorts the files in a folder into subfolders by type and date. This page is its
documentation.

## Install

::::tabs{sync="os"}
:::tab[macOS]
```sh
brew install tidy
```
:::

:::tab[Linux]
```sh
curl -fsSL https://example.com/tidy/install.sh | sh
```
:::

:::tab[Windows]
```powershell
winget install tidy
```
:::

:::tab[Python]
```sh
pipx install tidy-cli
```
:::
::::

Check that it works:

```sh
tidy --version
```

## Quick start

:::steps
1. Go to a messy folder: `cd ~/Downloads`.
2. See what tidy would do, without moving anything: `tidy --dry-run`.
3. Sort the files for real: `tidy`.
4. Changed your mind? `tidy undo` puts everything back.
:::

## Commands

| Command                           | What it does                                            |
| --------------------------------- | ------------------------------------------------------- |
| `tidy [folder]`                   | Sort the files in a folder; the current one by default. |
| `tidy undo`                       | Undo the last run.                                      |
| `tidy rules`                      | Show the rules tidy uses, and where they come from.     |
| `tidy watch [folder]` :badge[New] | Keep sorting new files as they arrive.                  |

## Options

| Option            | Default | What it does                                               |
| ----------------- | ------- | ---------------------------------------------------------- |
| `-n`, `--dry-run` | off     | Show the moves without making them.                        |
| `--by`            | `type`  | Group by `type`, `date` or `type,date`.                    |
| `--keep`          | none    | Leave files matching a pattern, such as `--keep "*.part"`. |
| `-q`, `--quiet`   | off     | Only print errors.                                         |

:::tip
Stop `tidy watch` with :kbd[Ctrl+C]. It finishes the move it is busy with first.
:::

## Configuration

tidy reads `tidy.toml` from the folder it sorts, then from your config folder. A file in the
folder wins.

:::filetree
- \~/.config/tidy/
  - **tidy.toml** your defaults
- \~/Downloads/
  - tidy.toml rules for this folder only
  - images/
  - documents/
  - …
:::

```toml title="tidy.toml" {3-4}
by = "type,date"

[folders]
images = ["jpg", "png", "heic"]
documents = ["pdf", "docx", "md"]
```

:::::details[Shell completion]
Add one line to your shell's startup file, then open a new terminal:

::::tabs{sync="shell"}
:::tab[zsh]
```sh
eval "$(tidy completion zsh)"
```
:::

:::tab[bash]
```sh
eval "$(tidy completion bash)"
```
:::

:::tab[fish]
```sh
tidy completion fish | source
```
:::
::::
:::::

:::caution
tidy never deletes files, but it does move them. Run it with `--dry-run` first on a folder that
other programs write to.
:::
