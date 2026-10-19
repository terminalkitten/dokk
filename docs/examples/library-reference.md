---
title: Library reference
description: The API reference of a made-up Python library, written by hand.
sidebar:
  order: 3
---

:::note[Example page]
The project, data and links on this page are made up, to show what dokk's components can do. It
does not document dokk itself.
:::

**slugkit** turns text into URL slugs. This is its API reference.

::install[slugkit]

```python
from slugkit import slugify

slugify("Héllo, Wörld!")  # "hello-world"
```

## slugify { #slugify }

```python
def slugify(text: str, *, separator: str = "-", max_length: int | None = None,
            lowercase: bool = True, stopwords: Iterable[str] = ()) -> str
```

Turn any text into a slug: accents are removed, everything that is not a letter or digit becomes
the separator, and repeated separators collapse into one.

| Parameter    | Type            | Default  | Description                                         |
| ------------ | --------------- | -------- | --------------------------------------------------- |
| `text`       | `str`           | required | The text to convert.                                |
| `separator`  | `str`           | `"-"`    | Put between words.                                  |
| `max_length` | `int \| None`   | `None`   | Cut the slug at a word boundary, at most this long. |
| `lowercase`  | `bool`          | `True`   | Lowercase the result.                               |
| `stopwords`  | `Iterable[str]` | `()`     | Words to leave out, such as `{"a", "the"}`.         |

**Returns** the slug, which may be empty. **Raises** `TypeError` when `text` is not a string.

```python {1}
>>> slugify("The Quick Brown Fox", stopwords={"the"})
'quick-brown-fox'
>>> slugify("A very long title indeed", max_length=12)
'a-very-long'
```

## unique_slug { #unique-slug }

```python
def unique_slug(text: str, taken: Container[str], **options) -> str
```

Like [`slugify`](#slugify), but adds `-2`, `-3` and so on until the slug is not in `taken`.
:badge[New in 2.1]

```python
taken = {"hello", "hello-2"}
unique_slug("Hello", taken)  # "hello-3"
```

## Slugifier { #slugifier }

```python
class Slugifier(separator: str = "-", **options)
```

Keep a set of options to reuse; calling the object slugifies.

```python
slug = Slugifier(separator="_", max_length=40)
slug("Hello World")  # "hello_world"
```

## Exceptions

`SlugError`
: Base class for slugkit's own errors.

`EmptySlugError`
: Raised by `slugify(..., allow_empty=False)` when nothing is left.

## Deprecated

:::caution[Removed in 3.0]
`slugkit.make_slug()` still works but warns. Use [`slugify`](#slugify): it takes the same
arguments, except `sep`, now called `separator`.
:::
