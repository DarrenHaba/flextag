# Schema Naming Conventions

## Tag Conventions for Schema Discoverability

When designing from scratch, use a consistent tagging pattern for schema-related sections:

```flextag
// Schema definition
[[#product]]: ftml-schema
name: str
price: float
[[/]]

// Data that follows the schema (both header AND body are validated)
[[#product name="MacBook" price=2499.99]]: ftml
description = "Professional laptop for developers"
specs = {
    cpu = "M3",
    ram = 16,
}
[[/]]
```

## Why Consistent Tags?

It makes discovery trivial. Load your FlexTag files and query:

```python
// Find all schema definitions
.filter(":ftml-schema")

// Find all data validated by schemas
.filter("#product :ftml")

// Find everything related to a domain
.filter("#product")
```

## Using Tagged Parameters for Organization

Tagged parameters let you organize sections with structured metadata:

```python
// All adapters
.filter("#adapter")

// OHLCV adapters specifically
.filter("type=#ohlcv")

// What adapter types exist?
view.filter("#adapter").values("type")
// Returns: ["#ohlcv", "#news", "#websocket", etc.]
```

## Not Enforced

This is a **convention**, not a requirement.

You can add schemas to existing data without restructuring:

```flextag
// Existing data (don't want to rename)
[[#adapter #ohlcv name="Yahoo Finance"]]: ftml
description = "Free market data"
[[/]]

// Add schema matching existing tags
[[#adapter #ohlcv]]: ftml-schema
name: str
[[/]]
```

The schema matches by tags. No restructuring needed.

## When to Use Conventions

**Use them when:**
- Designing a new system from scratch
- You want easy discoverability of all schemas
- You want consistent organization

**Skip them when:**
- Adding schemas to existing data
- The existing tag structure is already well-organized
- Renaming tags would break existing queries
