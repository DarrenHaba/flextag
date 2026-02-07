# FlexTag: Tag-Based Data Organization

> **Alpha Status**: Under active development - [Report Issues](https://github.com/DarrenHaba/flextag/issues) | [Send Feedback](https://github.com/DarrenHaba/flextag/issues).
---

## Hashtags Meet Data Integrity

FlexTag: Organize with `#hashtags`, validate with schemas, search like a search engine. One syntax from a single config to an entire directory.

**Why developers choose it:**

* **Data containerization** - Tag and organize data across sections, files and directories. Self-contained and composable.
* **Metadata-based organization** - Tags and parameters everywhere. Search files and sections uniformly.
* **Flexible filtering** - Select files and sections by tags and parameters, query as one dataset.
* **Format agnostic** - Mix FTML, JSON, YAML, text, binary. Search uniformly.
* **Schema validation** - Data integrity through metadata-based matching.
* **Don't repeat yourself** - One syntax mirrors across data, schemas, and queries.
* **Plain text always** - Human-readable, git-friendly, AI-friendly.

---

### Quick Example: Tag, Store, Search

See how FlexTag organizes data with hashtags:
```flextag
[[#database #production]]: ftml
host = "prod-db.example.com"
port = 5432
max_connections = 100
[[/]]

[[#database #development]]: ftml
host = "localhost"
port = 5432
max_connections = 5
[[/]]

[[#cache #production]]: ftml
host = "redis.example.com"
ttl = 3600
[[/]]
```

**Key Insight**: Tags on sections become your search queries. No separate query language to learn.

### Your First Python Search

Now let's search this data using the tags:
```bash
pip install flextag
```
```python
import flextag

# Load the file
view = flextag.load(path="config.ft")

# Search using the same hashtags
production = view.filter("#production")      # database + cache sections
databases = view.filter("#database")        # production + development
prod_db = view.filter("#database #production")  # exact match

print(prod_db[0].data)  # {'host': 'prod-db.example.com', 'port': 5432, ...}
```

The tags you write ARE your search queries. That's the whole idea.

### Hierarchical Tag Navigation

Tags support dot-separated hierarchy for deeper organization:
```flextag
[[#product.electronics name="Keyboard"]]: ftml
price = 79.99
description = "Mechanical keyboard"
[[/]]

[[#product.electronics.accessories name="USB Cable"]]: ftml
price = 9.99
length = "2m"
[[/]]

[[#product.clothing name="T-Shirt"]]: ftml
price = 19.99
size = "M"
[[/]]
```

**Three Search Modifiers**

| Modifier | Scope | Example |
|----------|-------|---------|
| `#tag` | Exact match | `#product.electronics` → keyboard only |
| `#tag*` | All descendants | `#product*` → keyboard, cable, t-shirt |
| `#tag+` | Immediate children | `#product+` → electronics, clothing |
```python
view.filter("#product*")                # everything
view.filter("#product+")                # top-level categories only
view.filter("#product.electronics*")    # keyboard + cable
```

Start broad, drill down. The hierarchy you design IS your navigation structure.

---

### Data Integrity: Schema Validation

FlexTag validates data using the same tag-matching system. Schemas are sections too:
```flextag
// Schema validates any section tagged #product or descendants
[[#product*]]: ftml-schema
name: str
price: float<min=0.01>
[[/]]

// Data automatically validated against matching schema
[[#product.electronics name="Keyboard"]]: ftml
price = 79.99
description = "Mechanical keyboard"
[[/]]

[[#product.clothing name="T-Shirt"]]: ftml
price = 19.99
size = "M"
[[/]]
```
```python
# Validation happens automatically on load
view = flextag.load(path="products.ft", validate=True)
```

**Key Points:**

* Schema uses `:` for type declarations, data uses `=` for values
* Schema `#product*` matches all sections tagged `#product` or deeper
* Extra fields like `description` and `size` are allowed - schemas only enforce what they declare
* Constraints work just like FTML: `price: float<min=0.01, max=99999.99>`

### Schema Layering

Multiple schemas can apply to the same section through tag matching:
```flextag
// Base schema for all products
[[#product*]]: ftml-schema
name: str
price: float
[[/]]

// Additional requirements for electronics
[[#product.electronics*]]: ftml-schema
warranty: str
sku: str
[[/]]
```

A `#product.clothing` section validates against the base schema (name, price).  
A `#product.electronics` section validates against both (name, price, warranty, sku).

No inheritance configuration needed - it's just tag matching.

---

### Python Type Hint Foundation

The core syntax comes from Python type hints, used consistently everywhere:
```
name: type = value
```

**Section Parameters** (compact, no spaces):
```flextag
[[#config version:int=2 debug:bool=false]]: ftml
```

**FTML Data Content** (readable spacing):
```ftml
version: int = 2
debug: bool = false
```

**FTML Schema** (types without values):
```ftml
version: int
debug: bool
```

Same pattern at every level. Only spacing and assignment context change.

---

### Mixed Content in One File

Each section declares its content type - mix any formats freely:
```flextag
[[#config]]: ftml
host = "localhost"
port = 5432
[[/]]

[[#endpoints]]: json
{"users": "/api/users", "products": "/api/products"}
[[/]]

[[#deploy]]: yaml
provider: aws
regions:
  - us-east-1
[[/]]

[[#notes]]: text
Remember to update deploy script before release.
[[/]]
```

Tags, parameters, filtering, and schemas work identically regardless of content type.

---

### File-Level Metadata

Files themselves can be tagged and searched using the same syntax:
```flextag
// Tag the entire FILE
[[#plugin #indicator version:str="2.0" author:str="team"]]: file-metadata
[[/]]

// Regular sections inside
[[#config]]: ftml
period = 20
color = "#2196F3"
[[/]]

[[#compute]]: python
def calculate(bars, period=20):
    return sum(bars[-period:]) / period
[[/]]
```

**File Filtering Uses the Same Tag Syntax**
```python
# Filter FILES by their metadata tags
view = flextag.load(dir="plugins/", filter_query="#indicator")

# Then filter SECTIONS within matched files
configs = view.filter("#config")
backends = view.filter("#compute")
```

Same hashtags. Same modifiers (`*`, `+`). Same search logic.  
Section filtering and file filtering use identical syntax.

---

### Indexing External Files

FlexTag can catalog external files without storing their content:
```flextag
[[#doc.report name="Q4 Sales" date="2025-12-01"]]: ftml
path = "/reports/q4-sales-2025.pdf"
author = "finance-team"
status = "final"
[[/]]

[[#doc.spec name="API v3" date="2025-11-15"]]: ftml
path = "/specs/api-v3.md"
owner = "backend-team"
status = "draft"
[[/]]
```
```python
drafts = view.filter("#doc* status=draft")
reports = view.filter("#doc.report*")
```

Organize any existing files - PDFs, images, CSVs, whatever - through tagging and metadata, without moving or converting anything.

---

## Advanced Features

FlexTag provides powerful capabilities for managing complex data:

* **Hierarchical Tags** - Tree-structured organization with precision queries
* **Schema Layering** - Multiple schemas apply through tag matching
* **Mixed Content** - Any format (FTML, JSON, YAML, text, binary) in one file
* **File Metadata** - Tag and filter entire files like sections
* **Parameter Matching** - Filter by tag AND parameter values
* **Plain Text Storage** - Git-friendly, human-readable, no special tools

---

## Installation
```bash
pip install flextag
```

Both `.flextag` and `.ft` file extensions are recognized.

---

## ⚠️ Alpha Status

FlexTag is in alpha (v0.4.0a1). Syntax may change before v1.0. Not recommended for production use.

## Contributing

Contributions welcome! Submit a Pull Request or open an issue.

## License

MIT License - see LICENSE file for details.