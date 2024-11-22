# FlexTag Reference System

## Core Concept
FlexTag uses a flat storage system where markers (#tags and .paths) are stored as simple lists.

## Storage Model

### Visual Syntax to Internal Storage
```
[[SEC #draft #review .docs.guide .docs.api]]
content
[[/SEC]]

Internally stored as:
{
    "tags": ["draft", "review"],
    "paths": ["docs.guide", "docs.api"],
    "content": "content"
}
```

### Key Points
- Tags and paths are just strings in lists
- No actual hierarchy exists in storage
- Dots in paths are part of the string
- Multiple paths allowed per section

## Search System

### Basic Search
```python
# Find by tag
doc.find("#draft")

# Find by path
doc.find(".docs")

# Combined search
doc.find("#draft .docs")
```

### Matching Rules
1. Tag Matching:
```python
doc.find("#draft")  # Exact match on "draft"
```

2. Path Matching:
```python
# Matches docs.guide, docs.api, etc
doc.find(".docs")  

# Only matches docs.guide
doc.find(".docs.guide", match_type="exact")
```

### Parameter Filtering
```python
# Combine markers with parameters
doc.find("#draft").priority.gt(5)
doc.find(".docs").modified.gt("2024-01-01")
```

## Real World Examples

### Documentation System
```
[[SEC #guide .docs.setup]]
Getting started...
[[/SEC]]

[[SEC #api .docs.reference]]
API details...
[[/SEC]]
```

Search examples:
```python
# Find all guides
guides = doc.find("#guide")

# Find all docs
docs = doc.find(".docs")

# Find setup guides
setup = doc.find("#guide .docs.setup")
```

## Best Practices

1. Tag Naming:
   - Use simple, descriptive tags
   - Consistent naming conventions

2. Path Structure:
   - Logical grouping: area.subarea
   - Keep paths shallow when possible

3. Search Strategy:
   - Start broad, then refine
   - Combine tags and paths for precision
   - Use parameters for complex filtering