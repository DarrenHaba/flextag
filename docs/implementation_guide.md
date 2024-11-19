# FlexTag Python Implementation Guide

## Document Operations
```python
from flextag import FlexTag

# Create or load document
doc = FlexTag()
doc = FlexTag.load("config.flextag")
doc = FlexTag.loads("[[SEC #tag]]content[[/SEC]]")
```

## Finding Sections
```python
# Search by markers
sections = doc.find("#draft .docs")

# Filter by parameters
sections = doc.find("#draft").priority.gt(5)

# Access sections
first = sections[0]           # List style
first = sections.first()      # Method style
last = sections[-1]          # Last section
last = sections.last()      # Method style
some = sections[1:3]         # Slice
```

## Content Access
```python
section = doc.find_one("#config")

# Get content
raw = section.raw_content
data = section.content       # Parsed based on fmt
text = section.parse("text") # Override format
```

## Adding/Modifying
```python
# Add section
doc.add(
    tags=["draft", "api"],
    paths=["docs.guide"],
    content="# API Guide",
    fmt="markdown"
)

# Update
section = doc.find_one("#config")
section.content = {"port": 8080}
section.add_tag("updated")
section.add_path("server.config")
```

## Parameter Filtering
```python
# Numeric
doc.find().count.gt(30)
doc.find().price.between(10, 100)

# String
doc.find().name.contains("test")
doc.find().status.in_(["draft", "review"])

# Date
doc.find().created.after("2024-01-01")

# Multiple filters
doc.find("#draft")\
   .priority.gt(5)\
   .status.eq("review")
```

## Error Handling
```python
try:
    section = doc.find("#missing").first()
except NotFound:
    print("Section not found")

try:
    data = section.parse()
except ParseError as e:
    print(f"Parse error: {e}")
```

## Save/Export
```python
doc.save("config.flextag")      # Save to file
text = doc.dumps()              # Get as string
```