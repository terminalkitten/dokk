---
title: Tool
description: A tool's parameters as a table, from its JSON schema.
sidebar:
  order: 6
---

`:::tool` documents a tool or function that a model can call. Paste its definition as a \`\`\`json
block: an OpenAI tool, an Anthropic tool or a bare JSON schema. dokk shows the parameters as a
table and keeps the JSON, collapsed, under it.

````md
:::tool
```json
{
  "name": "get_weather",
  "description": "The current weather for a city.",
  "input_schema": {
    "type": "object",
    "properties": {
      "city": {"type": "string", "description": "The city, such as \"Amsterdam\"."},
      "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "celsius"}
    },
    "required": ["city"]
  }
}
```
:::
````

:::tool
```json
{
  "name": "get_weather",
  "description": "The current weather for a city.",
  "input_schema": {
    "type": "object",
    "properties": {
      "city": {"type": "string", "description": "The city, such as \"Amsterdam\"."},
      "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "celsius"}
    },
    "required": ["city"]
  }
}
```
:::

The name and description come from the JSON; for a bare schema, write the name as the title,
`:::tool[get_weather]`. Other Markdown in the body shows above the table. Invalid JSON fails the
build with the line number.
