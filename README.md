# FlexTag

**Tags and sections for markdown.**

Your markdown files already hold structured content — configs, snippets,
prompts, parameters — trapped inside code blocks a program can't find. FlexTag
makes those blocks addressable: tag a fence with a YAML mapping, and every
tagged block in a file — or an entire folder of files — becomes one
filterable dataset.

There is no new format to learn. A FlexTag file is a plain markdown file that
renders normally everywhere — GitHub, Obsidian, your editor — because FlexTag
has **no syntax of its own**: metadata is YAML, structure is CommonMark, and
the library is only a loader.

## A file

````markdown
---
flextag: 0.5
tags: [config]
id: endpoints
---

# Service endpoints

Anything outside a tagged fence is ordinary markdown — prose, images, tables.

```yaml {tags: [database, env/production], id: prod-db}
host: prod-db.example.com
port: 5432
```

```yaml {tags: [database, env/development], id: dev-db}
host: localhost
port: 5432
```
````

## Loading it

```python
import flextag

view = flextag.load("configs/")             # one file, or a whole folder (recursive)

view.filter(tag="database")                 # sections by tag, across all files
view.filter(tag="database", id="prod-db")   # AND on any metadata key
view.filter(tag="production")               # path tags match any segment
view.values("id")                           # unique values -> dropdowns
view.files(tag="config")                    # FILES, selected by front matter
```

A `Section` is plain data — `tags`, `meta` (dict), `lang` (the fence language,
i.e. the body's type), `body` (verbatim), `file`, `line` — so any shape you
need is one comprehension away:

```python
{s.meta["id"]: s.body for s in view.filter(tag="database").sections}
```

## The whole format, four rules

1. **Front matter** (`---` YAML at the top) is the file's metadata. `tags:`
   tags the file; `flextag: 0.5` declares the format and version. Files
   without the marker still load — the marker states intent.
2. **A section** is a fenced code block whose info string is a YAML flow
   mapping: `` ```yaml {tags: [database], id: prod-db} ``. The `tags` key
   tags the section; every other key is metadata. A fence without a mapping
   is an illustration — prose, not data.
3. **Hierarchy** is a naming convention: `/` inside a tag
   (`env/production`). Filters match any segment; `view.children("env")`
   walks levels.
4. Malformed YAML is a **loud error** naming the file and line — never a
   silently smaller index.

YAML and CommonMark define everything else. FlexTag ships no parser, no
grammar, and no highlighter of its own; PyYAML is the single dependency.

## Install

```bash
pip install flextag==0.5.0a1
```

0.5 is a pre-release: pip only selects it when pinned, so nothing changes for
anyone on 0.4.

## The old format (0.4 and earlier)

Before 0.5, FlexTag was its own container format (`[[#tag ...]]: type` in
`.ft` files). That reader still works during migration:

```python
from flextag import legacy
view = legacy.load(path="old.ft")   # DeprecationWarning
```

It is frozen and will be removed in 0.6. If you need the old format
long-term, pin `flextag==0.4.0`.

## License

MIT — see [LICENSE](LICENSE).
Source, issues: https://github.com/techie-studios/flextag
