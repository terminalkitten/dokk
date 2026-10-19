---
title: Chat
description: A conversation with system, user and assistant turns.
sidebar:
  order: 5
---

`::::chat` holds the turns of a conversation: `:::system`, `:::user` and `:::assistant`. The
person's turns are bubbles on the right, the replies plain text next to an avatar, the way chat
apps and shadcn's [AI Elements](https://ui.shadcn.com/docs/ai-elements) show them.

````md
::::chat[Support bot]
:::system
You answer questions about dokk. Be brief.
:::
:::user
How do I add search?
:::
:::assistant[Claude]{icon="claude"}
Install the search extra and build again:

```sh
pip install "dokk[search]"
```
:::
::::
````

::::chat[Support bot]
:::system
You answer questions about dokk. Be brief.
:::
:::user
How do I add search?
:::
:::assistant[Claude]{icon="claude"}
Install the search extra and build again:

```sh
pip install "dokk[search]"
```
:::
::::

Every turn is Markdown, code blocks included. A `[title]` names the speaker; `icon` on the
assistant shows a vendor [logo](model.md#logos) instead of the sparkle. Turns also work on their
own, outside `::::chat`.
