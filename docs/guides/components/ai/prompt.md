---
title: Prompt
description: A prompt that readers can copy, or open in Claude or ChatGPT.
sidebar:
  order: 4
---

`:::prompt[Title]` shows a prompt with a **Copy** button and **Open in Claude** and **Open in
ChatGPT** links that start a chat with it. The body is Markdown; Copy and the links use it as written, Markdown included.

```md
:::prompt[Review a pull request]{role="system" model="any"}
You are a careful reviewer. For the diff below:

1. List bugs first, then risky changes.
2. Quote the line for each finding.
3. Skip style nits.
:::
```

:::prompt[Review a pull request]{role="system" model="any"}
You are a careful reviewer. For the diff below:

1. List bugs first, then risky changes.
2. Quote the line for each finding.
3. Skip style nits.
:::

## Variables

`{{ name }}` in the prompt becomes a field above the buttons. What the reader types fills it in on
the page, and in what Copy and the Open links send.

```md
:::prompt[Explain an error]{role="user"}
Explain this {{ language }} error and how to fix it:

{{ error }}
:::
```

:::prompt[Explain an error]{role="user"}
Explain this {{ language }} error and how to fix it:

{{ error }}
:::

## Attributes

`role`, `model`
: Badges in the header, such as `system` or `user`, and the model the prompt was written for.

`open`
: `open="false"` leaves out the Open in Claude and ChatGPT links, for prompts that only make
  sense in your own app.

The buttons need JavaScript and are hidden without it; the prompt itself is plain HTML.
Long prompts may be too long for a link: Copy always works.
