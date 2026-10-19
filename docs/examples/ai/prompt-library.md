---
title: Prompt library
description: A team's reusable prompts, ready to copy or open in a chat.
sidebar:
  order: 5
---

A shared page of prompts the team uses every week. Fill in the fields, then copy the prompt or
open it in Claude or ChatGPT. :badge[Example]{variant="secondary"}

## Code

:::prompt[Review a pull request]{role="user" model="any"}
You are a careful reviewer. For the diff below:
1. List bugs first, then risky changes.
2. Quote the line for each finding.
3. Skip style nits.

{{ diff }}
:::

:::prompt[Write tests]{role="user"}
Write pytest tests for this {{ language }} function. Cover the edge cases and one failure.

{{ code }}
:::

## Writing

:::prompt[Release notes]{role="user"}
Turn these commit messages into release notes for {{ product }} {{ version }}. Group them as
New, Fixed and Changed; leave out internal changes.

{{ commits }}
:::

:::prompt[Plain language]{role="user"}
Rewrite this for a reader who is not a developer. Keep it under {{ words }} words.

{{ text }}
:::

## For our own app

Prompts for the support bot; they only work in our app, so they have no Open links.

:::prompt[Support bot]{role="system" model="claude-sonnet" open="false"}
You answer questions about our product, using the help center articles you are given. Be brief
and friendly. When you are not sure, offer to hand over to a person.
:::
