---
title: Model comparison
description: Several models side by side in one table.
sidebar:
  order: 2
---

Put [model cards](model.md) in `::::models` to compare them in one table. A row is shown when at
least one model has that value; a missing one shows a dash.

```md
::::models
::model[Acme Large 2]{provider="Acme AI" input="3" output="15" context="200K" features="vision tools"}
::model[Acme Small 2]{input="0.25" output="1.25" context="200K" features="tools"}
::model[Acme Open 7B]{context="32K" license="Apache-2.0"}
::::
```

::::models
::model[Acme Large 2]{provider="Acme AI" input="3" output="15" context="200K" max_output="64K" features="vision tools reasoning"}
::model[Acme Small 2]{provider="Acme AI" input="0.25" output="1.25" context="200K" max_output="16K" features="tools"}
::model[Acme Open 7B]{provider="Acme AI" context="32K" license="Apache-2.0" released="2026-01"}
::::

It takes the same attributes as the model card; `icon` shows the vendor's [logo](model.md#logos)
next to the name. Wide tables scroll sideways on small screens.
