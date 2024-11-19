# FlexTag Parameter Filtering

Working on: Parameter type inference and filter API design

## Type Inference
Parameters automatically infer types from values:
```
[[SEC {
  count=42,          # int
  price=99.99,       # float
  name="test",       # string
  active=true,       # bool
  date="2024-01-01"  # date (ISO format)
}]]
```

## Filter API
```python
# Numeric
doc.find().count.gt(30)
doc.find().price.between(10, 100)
doc.find().count.in_([1, 2, 3])

# String
doc.find().name.contains("test")
doc.find().name.startswith("pre")
doc.find().name.matches("^test-\d+$")

# Boolean
doc.find().active.is_(True)

# Date
doc.find().date.before("2024-02-01")
doc.find().date.after("2024-01-01")

# Combining filters
doc.find("#draft")\
   .count.gt(30)\
   .active.is_(True)\
   .date.after("2024-01-01")
```

## Return Type
```python
sections = doc.find("#draft")  # Returns SectionList

# List operations
sections[0]       # First section
sections[-1]      # Last section
sections[1:3]     # Slice

# Chainable methods
sections.first()  # Same as [0]
sections.last()   # Same as [-1]
sections.at(1)    # Same as [1]
```