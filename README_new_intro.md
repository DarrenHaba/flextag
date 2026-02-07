# FlexTag

**A flat, tagged container format for storing multiple data formats with searchable metadata.**

## What is FlexTag?

FlexTag organizes content into tagged sections with rich metadata. Think of it as a queryable document container that can hold JSON, YAML, binary data, or any format in one file.

**Core principles:**
- ✅ Flat structure (no section nesting)
- ✅ Rich metadata (tags, paths, parameters)
- ✅ Multiple formats per file (JSON, YAML, FTML, text, binary)
- ✅ Powerful filtering by tags and paths

**Use FlexTag when you need:**
- Multiple config formats in one file
- Searchable, categorized content sections
- Override/merge behavior across files
- Mixed text and binary data

**Don't use FlexTag for:**
- Simple key-value config (use FTML, TOML, or JSON instead)
- Deeply nested hierarchical data (FlexTag is intentionally flat)

## Installation
```bash
pip install flextag
```

## Core Syntax

FlexTag sections use double brackets:
```flextag
[[#tag1 #tag2 @path.to.location param="value"]]: content_type
content goes here
[[/]]
```

**Section components:**
- `#tag` - Tags for categorization (exact match when filtering)
- `@path` - Paths for hierarchy (prefix match when filtering)
- `param="value"` - Key-value parameters
- `: content_type` - Format: `ftml`, `json`, `yaml`, `text`, `binary`
- `[[/]]` - Universal closing tag (no ID needed)

## Tags vs Paths: The Key Distinction

**This is the most important concept in FlexTag.**

### Tags (#) = Categories
Tags are for **flat categorization**. Use them to mark what TYPE of thing this is.
```flextag
[[#database #production]]: ftml
host = "prod-db.example.com"
[[/]]

[[#cache #production]]: ftml
host = "redis.example.com"
[[/]]

[[#database #development]]: ftml
host = "localhost"
[[/]]
```

Filtering by tag matches **exactly**:
```python
view.filter("#production")  # Returns 2 sections: database + cache
view.filter("#database")    # Returns 2 sections: production + development
```

### Paths (@) = Hierarchy
Paths are for **logical organization**. Use them to define WHERE something belongs.
```flextag
[[#database @config.storage]]: ftml
host = "prod-db.example.com"
[[/]]

[[#cache @config.storage]]: ftml
host = "redis.example.com"
[[/]]

[[#readme @docs]]: text
# Documentation
[[/]]
```

Filtering by path matches **prefix** (includes children):
```python
view.filter("@config")            # Returns 2 sections: database + cache
view.filter("@config.storage")    # Returns 2 sections: database + cache
view.filter("@docs")              # Returns 1 section: readme
```

### When to Use What

**Use tags for:**
- Environment: `#production`, `#development`, `#staging`
- Component type: `#database`, `#cache`, `#api`
- Status: `#draft`, `#published`, `#archived`

**Use paths for:**
- Logical grouping: `@config.database`, `@config.cache`
- Module organization: `@plugins.charts`, `@plugins.indicators`
- Document structure: `@docs.api`, `@docs.guides`

**Combine both:**
```flextag
[[#database #production @config.storage.primary]]: ftml
```

This section is:
- A database (tag)
- In production (tag)
- Located at config → storage → primary (path)

## Filtering

Combine tags and paths for powerful queries:
```python
import flextag

view = flextag.load(path="config.ft")

# Filter by tag (exact match)
prod_sections = view.filter("#production")

# Filter by path (prefix match)
config_sections = view.filter("@config")
storage_sections = view.filter("@config.storage")

# Combine with AND (space-separated)
prod_db = view.filter("#production #database")
prod_storage = view.filter("#production @config.storage")

# Use OR for alternatives
dev_or_staging = view.filter("#development OR #staging")

# Access sections
for section in prod_db.sections:
    print(section.content)
```

## Content Types

Sections can contain any format:
```flextag
[[#config]]: ftml
key = "value"
number = 42
[[/]]

[[#endpoints]]: json
{"users": "/api/users", "products": "/api/products"}
[[/]]

[[#deployment]]: yaml
provider: aws
regions:
  - us-east-1
[[/]]

[[#script]]: text
#!/bin/bash
echo "Deploy script"
[[/]]

[[#image]]: binary
<binary data here>
[[/]]
```

**Available types:**
- `ftml` - FlexTag's structured data format (TOML-like)
- `json`, `yaml`, `toml` - Standard data formats
- `text` - Plain text (preserves exact whitespace)
- `binary` - Raw bytes (returns `bytes` instead of `str`)

## Complete Example
```flextag
---meta---
[[#app @myapp version="1.0"]]
---/meta---

[[#database #production @config.storage.primary]]: ftml
host = "prod-db.example.com"
port = 5432
credentials = {
    username = "app_user",
    password = "secret"
}
[[/]]

[[#database #development @config.storage.primary]]: ftml
host = "localhost"
port = 5432
[[/]]

[[#cache #production @config.storage.cache]]: json
{
    "host": "redis.example.com",
    "port": 6379,
    "ttl": 3600
}
[[/]]

[[#readme @docs]]: text
# My Application

Production-ready application with database and cache.
[[/]]
```

**Query it:**
```python
import flextag

view = flextag.load(path="config.ft")

# Get production database
prod_db = view.filter("#production #database").sections[0]
print(prod_db.content["host"])  # "prod-db.example.com"

# Get all storage configs (database + cache)
storage = view.filter("@config.storage")
print(len(storage.sections))  # 3 sections

# Get all production configs
prod_configs = view.filter("#production")
for section in prod_configs.sections:
    print(section.tags, section.content)
```

## Common Mistakes

### ❌ Don't try to nest sections

FlexTag sections are always flat:
```flextag
[[#parent]]
  [[#child]]  # WRONG - can't nest sections
  [[/]]
[[/]]
```

**Instead, use paths for hierarchy:**
```flextag
[[#parent @app]]: text
parent content
[[/]]

[[#child @app.components]]: text
child content
[[/]]

# Query parent and all children
view.filter("@app")  # Returns both sections
```

### ❌ Don't confuse tags with paths
```flextag
# WRONG - using tags for hierarchy
[[#config #config.database]]: ftml

# RIGHT - paths for hierarchy, tags for categories
[[#database @config.database]]: ftml
```

### ❌ Don't use FlexTag for simple configs

If you just need key-value pairs, use FTML or JSON directly. FlexTag is for when you need multiple sections with rich metadata.

## Next Steps

- **File-level blocks**: Use `---meta---` and `---schema---` for file metadata
- **Parameters**: Add typed parameters to sections
- **Loading**: Load from files, directories, or strings
- **FTML**: Learn the structured data format designed for FlexTag

## WARNING: EXPERIMENTAL

FlexTag is in alpha (v0.4.0a1). Syntax may change before v1.0. Don't use in production.