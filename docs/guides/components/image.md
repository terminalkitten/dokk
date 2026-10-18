---
title: Image
description: An image with a caption that opens full size when clicked.
sidebar:
  order: 9
---

`::image[Alt text]{src="..."}` shows an image that opens full size in a dialog when clicked.
Esc, the close button or a click outside closes it. The alt text is required. Optional:
`caption`, and `width` and `height` to reserve space while the image loads.

```md
::image[The Writing pages guide in dokk]{src="img/example.jpg" caption="Click to enlarge."}
```

::image[The Writing pages guide in dokk]{src="img/example.jpg" caption="Click to enlarge."}

For a caption with Markdown, write it as the body:

```md
:::image[The Writing pages guide in dokk]{src="img/example.jpg"}
The [Writing pages](../writing.md) guide, in light mode.
:::
```

Like Markdown images, the path is relative to the page, a missing file is reported as a broken
link, and the image loads only when it scrolls into view. Without JavaScript, clicking opens the
image file itself.
