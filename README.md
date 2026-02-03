# FlexTag

FlexTag is a bracket-based markup language with sections, schema validation, and rich querying capabilities. Built to work seamlessly with FTML for advanced data storage and validation.

## ⚠️ EXPERIMENTAL WARNING ⚠️

> FlexTag is currently in the alpha stage (v0.4.0a1) with experimental syntax that may change significantly between versions. Do not use in production systems or with critical data until a stable 1.0 release.

## Installation

Install from PyPI:

```bash
pip install flextag
```

# FlexTag and FTML Quick Start

This document provides syntax examples for FlexTag (container format) and FTML (data format) to help understand how they both work together.

## FlexTag Section Syntax

FlexTag uses double bracket `[[]]` sections to encapsulate content:

```
[[section_id #tag1 #tag2 @path.to.something param="value"]]: content_type
content goes here
[[/section_id]]
```

### Section Components:

- **Section ID**: `section_id` - Identifier for the section
- **Tags**: `#tag1 #tag2` - Categorization labels (start with `#`)
- **Paths**: `@path.to.something` - Hierarchical organization (start with `@`)
- **Parameters**: `param="value"` - Key-value attributes
- **Content Type**: `: content_type` - Format specifier (ftml, json, yaml, toml, text, binary)
- **Content**: Everything between opening and closing markers
- **Closing Tag**: `[[/section_id]]` - Must match opening ID

### Multiple Tags and Paths:

```flextag
[[config #production #v2 @app.backend @service.api ver="2.1" active=true]]: ftml
// FTML content here.
[[/config]]
```

## FTML Data Syntax

FTML is a data format with TOML-like syntax:

### Key-Value Pairs:

```ftml
key = "string value"
number = 42
boolean = true
null_value = null
```

### List/Arrays:

```ftml
// Inline array
tags = ["web", "api", "backend"]

// Multiline array
environments = [
    "development",
    "staging", 
    "production"
]
```

### Objects/Dict:

```ftml
// Inline object
user = {name = "Alice", role = "admin"}

// Multiline object
database = {
    host = "localhost",
    port = 5432,
    credentials = {
        username = "app_user",
        password = "secret"
    }
}
```

### Comments:

```ftml
// This is an FTML comment
name = "MyApp"  // Inline comment
```

## Content Type Examples

FlexTag can contain multiple content types:

### FTML:

```flextag
[[config]]: ftml
name = "MyApp"
version = "1.0.0"
features = ["auth", "api", "admin"]
database = {
    host = "localhost",
    port = 5432
}
[[/config]]
```

### JSON:

```flextag
[[endpoints]]: json
{
    "users": "/api/users",
    "products": "/api/products",
    "orders": {
        "create": "/api/orders/create",
        "list": "/api/orders/list"
    }
}
[[/endpoints]]
```

### YAML:

```flextag
[[deployment]]: yaml
provider: aws
regions:
  - us-east-1
  - eu-west-1
resources:
  cpu: 2
  memory: 4G
[[/deployment]]
```

### TOML:

```flextag
[[cache]]: toml
ttl = 3600
max_size = "2GB"

[cache.redis]
host = "redis.example.com"
port = 6379
[[/cache]]
```

### Text:

```flextag
[[response #note]]: text
This is unstructured text content.
It preserves formatting and whitespace exactly as written.

This is great for text responses, code snippets,
markdown content, HTML, CSS, Javascript, etc,
or any content where exact formatting matters.
[[/response]]
```

```flextag
[[script #python]]: text
import os

print("This is a python script")
if os.environ.get("DEBUG") == "true":
    print("Debug mode enabled")
[[/script]]
```

### Binary:

```flextag
[[data]]: binary
Raw byte content here - returns bytes instead of str.
Useful for embedding binary data that needs to preserve
exact byte values through surrogateescape encoding.
[[/data]]
```

## Common FlexTag Patterns

### Environment-specific Configs:

```
[[database #production]]: ftml
host = "prod-db.company.com"
[[/database]]

[[database #development]]: ftml
host = "localhost"
[[/database]]
```

### Hierarchical Configs:

```
[[server @app.backend]]: ftml
port = 8080
[[/server]]

[[client @app.frontend]]: ftml
port = 3000
[[/client]]
```

### Multiple Formats:

```
[[auth]]: ftml
enabled = true
provider = "oauth"
[[/auth]]

[[auth_endpoints]]: json
{
    "login": "/auth/login",
    "logout": "/auth/logout" 
}
[[/auth_endpoints]]
```

## Filtering Syntax

FlexTag supports filtering by tags, paths, and parameters:

```python
# Filter by tag
production_configs = view.filter("#production")

# Filter by path
backend_configs = view.filter("@app.backend")

# Filter by parameter
v2_configs = view.filter('version="2.1"')

# Combine filters
prod_backend = view.filter("#production @app.backend")  # Implicit AND - like search engines
backend_api = view.filter("#api @app.backend")          # Filter by both tag and path

# Use OR explicitly when needed
dev_or_staging = view.filter("#development OR #staging")  # Explicit OR

# Complex combinations
prod_backend_or_frontend = view.filter("#production @app.backend OR @app.frontend")
cache_prod_staging = view.filter("@database.cache #production OR #staging")
v2_configs = view.filter('#v2 OR ver>=2.0 ver<3.0')
```

## Accessing Sections

Access sections directly through the view:

```python
import flextag

config = """
[[database #production]]: yaml
host: prod-db.company.com
port: 5432
[[/database]]

[[database #development]]: yaml
host: localhost
port: 5432
[[/database]]
"""

view = flextag.load(string=config)

# Access all sections
for section in view.sections:
    print(section.id, section.content)

# Filter by tag
prod_sections = view.filter("#production")
for section in prod_sections.sections:
    print(section.content["host"])  # prod-db.company.com

# Get sections by ID
db_sections = [s for s in view.sections if s.id == "database"]
print(len(db_sections))  # 2
```

### Loading from Files and Directories

```python
import flextag

# Load from a single file
view = flextag.load(path="config.flextag")

# Load from multiple files
view = flextag.load(path=["config.flextag", "settings.ft"])

# Load from a directory (recursively searches subdirectories by default)
view = flextag.load(dir="plugins/")

# Load from directory without recursion (top-level only)
view = flextag.load(dir="plugins/", recursive=False)

# Load from multiple directories
view = flextag.load(dir=["plugins/indicators/", "plugins/drawings/"])
```

Both `.flextag` and `.ft` file extensions are recognized.

## Complete Document Example

```
[[app_config #production @app]]: ftml
name = "MyApp"
version = "2.1.0"
debug = false
[[/app_config]]

[[database #production @database.primary]]: yaml
host: prod-db.company.com
port: 5432
[[/database]]

[[cache #production @database.cache]]: json
{"host": "redis.company.com", "port": 6379}
[[/cache]]

[[deploy_script #production @script.bash]]: text
#!/bin/bash
docker build -t myapp .
kubectl apply -f k8s/production/
[[/deploy_script]]
```

Remember: FlexTag uses `[[...]]` for sections, while FTML uses `key = value` syntax with `{}` for objects and `[]` for arrays.

## Parameter Type System

FlexTag parameters in section headers support both automatic type inference and explicit type annotations.

### Automatic Type Inference

By default, parameter values are automatically converted to appropriate types:

```flextag
[[section_id 
  name="admin"          // String (requires double quotes)
  count=42              // Integer
  score=3.14            // Float
  active=true           // Boolean (true or false)
  settings=null         // Null value
]]
```

Types are inferred as follows:
- `"value"` → String (double quotes required)
- `42` → Integer
- `3.14` → Float
- `true` or `false` → Boolean
- `null` → Null

### Explicit Type Annotations

For more control, you can explicitly specify parameter types using the colon syntax:

```flextag
[[section_id 
  name:str="admin"      // Explicitly a string
  count:int=42          // Explicitly an integer
  score:float=3.14      // Explicitly a float
  active:bool=true      // Explicitly a boolean
]]
```

Explicit type annotations are useful when:
- You want to enforce a specific type
- You need to override the automatic type inference
- You need type conversion (e.g., `count:float=42` gives `42.0`)

### Supported Types

FlexTag supports these parameter types:

| Type     | Aliases     | Examples                 |
|----------|-------------|--------------------------|
| `str`    | `string`    | `name:str="John"`        |
| `int`    | `integer`   | `count:int=42`           |
| `float`  |             | `score:float=3.14`       |
| `bool`   | `boolean`   | `active:bool=true`       |
| `null`   |             | `value:null=null`        |

### Nullable Types

Add a question mark after the type to allow null values:

```flextag
[[section_id
  name:str="John"       // Must be a string, cannot be null
  age:int?=null         // Can be integer or null
  score:float?=3.14     // Can be float or null
]]
```

### Type Conversion

Explicit type annotations can convert between compatible types:

```flextag
[[section_id
  count:int="42"        // String "42" converted to integer 42
  id:str=123            // Number 123 converted to string "123"
  amount:float=42       // Integer 42 converted to float 42.0
]]
```

### Working with Types in Code

When accessing parameters in Python code, the types are preserved:

```python
import flextag

data = '''
[[config name:str="app" version:float=1.5 active:bool=true]]
Settings here
[[/config]]
'''

view = flextag.load(string=data)
params = view.sections[0].parameters

print(type(params['name']))    # <class 'str'>
print(type(params['version'])) # <class 'float'>
print(type(params['active']))  # <class 'bool'>
```

### Best Practices

1. **Use Automatic Inference** for simple cases where the type is obvious
2. **Use Explicit Types** when type safety is important or conversion is needed
3. **Use Nullable Types** (`type?`) when parameters might be null
4. **Be Consistent** with your approach to typing across your document

## ⚠️ EXPERIMENTAL WARNING ⚠️

> The FlexTag Schema System is highly experimental. It will be refined and likely completely rebuilt in future versions.

# FlexTag and FTML Schema Systems

FlexTag uses two distinct but complementary schema systems:

1. **FlexTag Schema**: Controls section structure and metadata
2. **FTML Schema**: Validates structured data within FTML sections

## FlexTag Schema System

The FlexTag schema system provides validation for the **document structure**:

- Section **order and repetition**
- Required **metadata** (IDs, tags, paths, parameters)
- Section **content types** (text, binary, or markup types like ftml)

### FlexTag Schema Definition

A FlexTag schema is defined in a special section at the start of a document:

```flextag
[[]]: schema
[notes #draft /]?: text         # Optional section with specific tag
[config #settings]: ftml        # Required section with FTML content
[entry #data @items /]*: ftml   # Zero or more sections with specific metadata
[[/]]
```

### FlexTag Schema Syntax

Each line defines a rule for a section:

```
[section_id #tags @paths param=val /]?: content_type
```

With repetition modifiers:
- No symbol: Exactly one required occurrence
- `?`: Optional (0 or 1 occurrence)
- `*`: Zero or more occurrences
- `+`: One or more occurrences

## FTML Schema System

The FTML schema system validates **structured data** within FTML sections:

- **Type safety** for fields (str, int, float, bool, etc.)
- **Constraints** for values (min, max, pattern, etc.)
- **Unions** for multiple allowed types
- **Default values** for optional fields

### FTML Schema Definition

FTML schemas can be defined in a schema section:

```flextag
[[]]: schema
[config]: ftml
  name: str<min_length=2>
  age?: int<min=0> = 18
  tags: [str]<min=1>
  address: {
    street: str,
    city: str,
    zip: str<pattern="[0-9]{5}">
  }
[[/]]
```

### FTML Schema Types

FTML schemas support various types:

- **Scalar types**: `str`, `int`, `float`, `bool`, `null`, `any`, `date`, `time`, etc.
- **Collection types**: Lists `[type]` and objects `{field: type}`
- **Constraints**: In angle brackets `<min=0, max=100>`
- **Union types**: With pipe operator `str | int | null`
- **Optional fields**: With question mark `field?:`
- **Default values**: With equals sign `field: type = default`

## Working with Both Schema Systems

When using FlexTag with FTML content:

1. **Define FlexTag schema** to validate document structure:
   ```flextag
   [[]]: schema
   [config]: ftml
   [logs]*: text
   [[/]]
   ```

2. **Define FTML schema** to validate structured data:
   ```flextag
   [[]]: schema
   [config]: ftml
   // FTML schema here
   user: {
     name: str,
     age: int<min=0>
   }
   [[/]]
   ```

3. **Create sections** following the schemas:
   ```flextag
   [[config]]: ftml
   user: {
     name: "John",
     age: 30
   }
   [[/config]]
   
   [[logs]]: text
   System started at 2023-01-01
   [[/logs]]
   ```

## Validation Process

When you call `FlexTag.load(..., validate=True)`, the system:

1. Validates the FlexTag document structure against the FlexTag schema
2. For each FTML section, validates its content against the FTML schema (if provided)

This layered approach allows comprehensive validation from document structure down to individual data fields.



## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.