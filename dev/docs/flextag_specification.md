# FlexTag Specification

## Overview
FlexTag is a lightweight markup language designed for structured content with powerful validation capabilities. It combines the simplicity of **flat, section-based** organization (using `[[...]]` blocks) with the flexibility of optional **YAML** content when needed.

**Core concepts**:
- **Containers**: Logical units (typically files) that hold related sections. A container can be loaded from a `.flextag` file, a `.ft` file, or from a raw string.
- **Sections**: Self-contained blocks of content with metadata, enclosed in double brackets `[[...]]`.
- **Metadata**: IDs, tags, paths, and parameters for organization and filtering.
- **Content Types**:
   - **raw** (default) for unstructured raw data.
   - **yaml** for structured data (parsed automatically).
- **Schema**: Optional validation of structure, metadata, and (if desired) detailed YAML fields.

When you parse a file or string with FlexTag, it is broken down into **containers** and **sections**:
1. **Container** metadata (`[[]]: container`) for file-level info.
2. **Defaults** metadata (`[[]]: defaults`) to set shared tags/paths/params for subsequent sections.
3. **Schema** (`[[]]: schema`) that defines how the remaining sections should appear, their repetition, required tags, etc.
4. **User sections**: `[[id]]`, either raw or YAML.

Example container:
```flextag
// Container metadata
[[]]: container
[my_container #documentation .specs version=1.0 /]
[[/]]

// Container defaults
[[]]: defaults
[default_status="draft" __encoding="utf-8" /]
[[/]]

// Schema (optional)
[[]]: schema
[notes #log /]?: raw
[config #settings]: yaml
[[/]]

// Actual content sections
[[notes #log /]]: raw
Here is a raw text block
[[/notes]]

[[config #settings]]: yaml
theme: "dark"
fontSize: 16
features:
  - "search"
  - "export"
[[/config]]
```

**Key features**:
- Flat structure with optional nested IDs like `[[user.profile]]`.
- Clear, readable syntax for both raw and YAML sections.
- Powerful schema system for validating the presence and repetition of sections, plus advanced YAML checks if desired.
- Flexible metadata for organization, filtering, and defaults.


## Basic Section Structure
Each FlexTag **section** consists of:
1. A **header**: `[[id #tags .paths params]]: type`
2. **Content** (lines until the close tag)
3. A **footer**: `[[/id]]`

### Example
```flextag
// Basic section with default raw type
[[doc]]
Any raw text content thet
spans over multiple lines
[[/doc]]

// Section with explicit YAML type
[[config]]: yaml
theme: "dark"
features:
  - "search"
  - "export"
[[/config]]
```

### Section Headers
The **section header** can include:
- **ID** (e.g. `[[user]]`, `[[user.profile]]`)
- **Tags**: `#someTag`
- **Paths**: `.some.path`
- **Parameters**: `key=value`
- **Type Declaration**: `: raw` or `: yaml` (default is `raw` if omitted)
- **Self-closing**: `[[something /]]` if no content is needed

Example:
```flextag
[[user.profile #draft .users rating=4.5]]
Profile content
[[/user.profile]]

[[metadata language="en" version=2 /]]
```

### Content Types
FlexTag supports **two** primary content types:
1. **raw** (default)  
   Preserves raw lines, whitespace, and indentation. FlexTag does not parse it any further.
   ```flextag
   [[notes]]
   This is just a raw text block
   with multiple lines
   [[/notes]]
   ```

2. **yaml**  
   Automatically parsed by PyYAML into Python objects (lists, dicts, strings, etc.).
   ```flextag
   [[config]]: yaml
   debug: true
   items:
     - "apple"
     - "banana"
   [[/config]]
   ```

**Access**:
```python
section.content  # returns raw text (str) for "raw" sections
                # returns parsed Python data (dict/list/etc.) for "yaml" sections
```


## Metadata System

Metadata is a simple string, with values separated by spaces.

`nested.id #tag .nested.path pram="value"`

It's a pattern reused throughout the framework. 

Metadata strings appear in sections:
```flextag
# Use in raw section hedders:
[[section_id #my_tag .my.path my_pram="My Value"]]: raw
Raw text here.
[[/]]

# Use in yaml section hedders:
[[section_id #my_tag .my.path my_rate=49.99]]: yaml
YAML here
[[/]]

# Use as container metatadata
[[]]: container
# Metadata used to dynamically filter out containers
[container_id #container_tag container_version="1.2"]
[[/]]
```

Metadata strings are the base for filter query:
```python
import FlexTag

# Only load containers with specified metadata. 
# todo (Need to check make sure this only opens up the file and reads the first Section, which should be of type container..)
view = FlexTag.load(["file1.ft", "file2.ft"], filter_query='container_id container_version="1.2"')

# Once loaded filter down sections
view.filter("section_id my_rate>=40.00 my_rate<=65.0")

# Here we can copy and paste the header into the filter, as is.
view.filter('section_id #my_tag .my.path my_pram="My Value"')
# This would definitely return that section, And if any section shared the exact same metadata parameter, it would return them as well. 


# todo Add more examples or clear them up. .
```





Sections can include metadata in their headers, separated by spaces:
- ID: First item without prefix (e.g., `user.profile`)
- Tags: Start with # (e.g., `#draft`)
- Paths: Start with . (e.g., `.blog.posts`)
- Parameters: key=value pairs



### Section IDs
- Each section can optionally have an ID, e.g. `[[user]]`.
- Flat IDs don't use/need a dot: `[[id]]`, `[[user_id]]`.
- Nested IDs use a dot: `[[user.profile]]`, `[[user.profile.settings]]`.
- If an ID is `user.profile`, FlexTag can store it in a nested `FlexMap` structure for easy access.
- IDs should be lowercase and spaced replace with underscores. 

### Tags
- Tags begin with `#` and are used for categorization or filtering.
- You can have multiple tags per section, e.g. `[[article #draft #tutorial]]`.
- Tags should be lowercase and spaced replace with underscores.

### Paths
- Paths begin with `.` and represent hierarchical labels, e.g. `[[photo .albums.vacation]]`.
- Useful for grouping or filtering, e.g. `.finance.q1.expenses`.
- Paths should be lowercase and spaced replace with underscores.


### Parameters
- Key-value pairs in the header, e.g. `[[section_name="John" age=30]]`.
- Type is inferred automatically (`string`, `int`, `float`, `bool`, or `null`).
- Key names should be lowercase and spaced replace with underscores.

### Parameter values are automatically typed:
- `key="value"` → string (must use double quotes)
- `key=42` → integer
- `key=3.14` → float
- `key=true` or `key=false` → boolean
-  key=null → null (no value)

## Schema System
**Schemas** define rules for the sections **after** them, including:
- **Metadata validation**:
  - Must match ID, required tags/paths, or parameter keys/values
  - Must appear in the correct order or repetition
- **Repetition rules** for sections:
  - **`?`** means optional (0 or 1 occurrence)
  - **`*`** means 0 or more occurrences
  - **`+`** means 1 or more occurrences
  - No symbol => exactly 1 occurrence
- **Content type**: Usually `yaml` or `raw`.
  - If `yaml`, you can do further checks on fields if desired.

Schema symbol table:

| Symbol | Meaning                    |
|--------|----------------------------|
| ?      | Optional (0 or 1 occurrence)|
| *      | Zero or more occurrences   |
| +      | One or more occurrences    |
| none   | Exactly one occurrence     |


### Defining a Schema
Place a `[[id]]: schema` block near the start of the file (after `container` or `defaults`), then list each section rule line by line. For example:

```flextag
[[]]: schema
[notes #draft /]?: raw
[config #settings]: yaml
[entry #data .items /]*: yaml
[[/]]
```

Each bracket line:
- `[notes #draft /]? : raw` means:
  - Section ID must be `notes`
  - Must have tag `#draft`
  - Self-closing slash in the header is allowed, but not required
  - `?` => optional (0 or 1 times)
  - `: raw` => content is raw text (default if omitted)
- `[config #settings]: yaml` => exactly 1 occurrence, must have `#settings` tag, content is `yaml`.
- `[entry #data .items /]*: yaml` => 0 or more occurrences, must have `#data`, path `.items`, content is `yaml`.

### Validation Flow
When you call `FlexTag.load(..., validate=True)`, the library:
1. Reads the `schema` section (if any) and parses these lines into **schema rules**.
2. Reads user sections in order, matching them against the rules:
   - If a rule is `notes? : raw` and the next actual section is `[[notes]]: raw`, it's a match. If there's no `notes` section, that is also fine because it's `?`.
   - If a rule is `[entry]*: yaml`, then all subsequent sections named `entry` are matched until we hit a new rule or end of file.
3. Raises a `SchemaSectionError` if a required section is missing or if an unexpected section appears.
4. Raises a `SchemaTypeError` if the content type doesn't match. (e.g. if the rule says `yaml` but the actual user section has `: raw`).
5. If you do advanced checks on the YAML fields, it can raise further errors (e.g. missing keys, wrong type).

## Container/File Structure

## Head Sections
There are up to three **head sections**, each bracketed as `[[ ]]: type`. They must appear (if they appear at all) in this order:
1. **container**  
2. **defaults**  
3. **schema**  

### Container
`[[]]: container` sets metadata for the entire file/container:
```flextag
[[]]: container
[my_file_id #container .top param=123 /]
[[/]]
```
Any lines within it can set the container's ID, tags, paths, or parameters. For example:
```flextag
[[]]: container
[global_id #global_tag debug=true]
some_other_key=456
[[/]]
```
That means your top-level container might get:
```
container.id = "global_id"
container.tags = ["#global_tag"]
container.parameters = {"debug": True, "some_other_key": 456}
```

### Defaults
`[[]]: defaults` sets default metadata that applies to **all subsequent sections** unless overridden:
```flextag
[[]]: defaults
[default_id #default_tag status="draft" /]
[[/]]

// Now all user sections have .id=default_id, #default_tag, status="draft"
// unless they specify their own overrides
[[notes]]
Some text
[[/notes]]
```

### Schema
`[[]]: schema` holds extended rules for the sections that follow.
**Each** line in the schema typically looks like:
```
[section_id #tags .paths param=val /]?: yaml
```
**Repetition** is controlled by `?`, `*`, `+`, or none for exactly one:
- `?` => optional (0 or 1)
- `*` => zero or more
- `+` => one or more
- no symbol => exactly one

**Example**:
```flextag
[[]]: schema
[notes #draft /]?: raw
[config #settings]: yaml
[[/]]

[[notes #draft /]]: raw
Hello
[[/notes]]

[[config #settings]]: yaml
theme: dark
[[/config]]
```
If `validate=True`, FlexTag will ensure `notes` can appear at most once, `config` exactly once, etc.


## Query System

After loading, you can filter sections/containers by ID, tags, paths, or parameters.
```python
view = FlexTag.load("doc.flextag")

# Filter sections that have tag '#draft' and param "rating=5"
draft_secs = view.filter("#draft rating=5", target="sections")
```
**Operators**:
- `#tag` => match tag
- `.path` => match path
- `key=val`, `key>val`, `key<val`, etc. => param checks
- `OR` => logical OR of tokens
- `!#tag` => negate

## Configuration and Settings

### Global Settings
```python
settings = FlexTagSettings()
settings.allow_directory_traversal = False
settings.max_section_size = 1024 * 1024
settings.encoding = 'utf-8'

view = FlexTag.load("file.ft", settings=settings)
```

### Defaults vs. Per-Section
A `[[ ]]: defaults` block can set tags/paths/params for subsequent sections.  
Section-level metadata overrides these defaults.  
Global settings apply if no overrides are found.

## API Usage

### Loading Content
```python
from flextag import FlexTag

# Load from file:
view = FlexTag.load("file.flextag")

# Load from directory (includes .flextag and .ft):
view2 = FlexTag.load("mydir/")

# Load from raw string:
my_string = \"\"\"[[id]]Some content[[/id]]\"\"\"
view3 = FlexTag.load(string=my_string)
```

### Filtering
```python
filtered_view = FlexTag.load("data.ft", filter_query="#draft")
```
Only sections (or containers) matching `#draft` appear in `filtered_view`.

### Working with Sections
```python
print(len(view.sections))
sec = view.sections[0]
print(sec.id, sec.tags, sec.paths, sec.parameters)
print(sec.content)       # parsed if :yaml, raw if :raw
print(sec.raw_content)   # always the raw string
```

### Working with Containers
```python
for c in view.containers:
    print("Container ID:", c.id)
    print("Tags:", c.tags)
    for s in c.sections:
        print("Section ID:", s.id, "Type:", s.type_name)
        # ...
```

### FlexMap
You can convert to a `FlexMap` for ID-based or nested-ID-based access:
```python
fm = view.to_flexmap()

# If a section ID is "items", you can do:
fm["items"][0].content   # If multiple sections share "items", index them

# If an ID is "user.profile", you'd do:
fm["user"]["profile"][0].content
```

## Best Practices

1. **Keep It Flat**  
   Avoid deep nested IDs if possible. Break up large docs into multiple sections or files.

2. **Choose Types Wisely**  
   - Use `raw` for large unstructured blocks.
   - Use `yaml` if you need structured data or advanced keys.

3. **Schema Design**  
   - Start simple, define only the sections you truly need.
   - Use repetition symbols (`?`, `*`, `+`) for optional or repeated sections.
   - Consider advanced YAML checks if necessary (e.g., required keys in `yaml`).

4. **Defaults**  
   - Use a `[[]]: defaults` block for shared tags/paths/params if many sections share them.

5. **Organization**  
   - Use consistent ID naming (e.g. `user.profile`).
   - Tag each section for easy filtering (`#draft`, `#published`, etc.).
   - Keep file-level metadata minimal but informative in `container` and `defaults`.
