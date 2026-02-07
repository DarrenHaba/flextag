# Schema Naming Conventions

## The `#schema.` Prefix Convention

When designing from scratch, prefix schema-related tags with `#schema.`:

```flextag
// Schema definition
[[#schema.product*]]: ftml-schema
name: str
price: float
[[/]]

// Data that follows the schema (both header AND body are validated)
[[macbook #schema.product name="MacBook" price=2499.99]]: ftml
description = "Professional laptop for developers"
specs = {
    cpu = "M3",
    ram = 16,
}
[[/]]
```

## Why This Convention?

It makes discovery trivial. Load your FlexTag files and query:

```python
// Find all schema definitions
.filter("#schema* :ftml-schema")

// Find all data that uses schemas
.filter("#schema* :ftml")

// Find everything schema-related (definitions + data)
.filter("#schema*")
```

## Drilling Down

The nested tag structure lets you explore hierarchically:

```python
// All top-level schema categories
.filter("#schema+")
// Returns: #schema.product, #schema.adapter, #schema.settings, etc.

// All product-related sections
.filter("#schema.product*")
// Returns: sections with #schema.product, #schema.product.laptop, etc.

// Just laptop data
.filter("#schema.product.laptop :ftml")
```

## Not Enforced

This is a **convention**, not a requirement.

`#schema` is not a built-in or internal tag — it's just a recommended prefix. You can add schemas to existing data without restructuring:

```flextag
// Existing data (don't want to rename)
[[yahoo #adapter #ohlcv name="Yahoo Finance"]]: ftml
description = "Free market data"
[[/]]

// Add schema matching existing tags
[[#adapter #ohlcv]]: ftml-schema
name: str
[[/]]
```

The schema matches by tags. No restructuring needed.

## When to Use the Convention

**Use it when:**
- Designing a new system from scratch
- You want easy discoverability of all schemas
- You want hierarchical organization

**Skip it when:**
- Adding schemas to existing data
- The existing tag structure is already well-organized
- Renaming tags would break existing queries
