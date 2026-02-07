# Dual Tag Paths

## The Pattern

A section can have multiple tag hierarchies:

```flextag
[[macbook #schema.product.laptop #product.laptop name="MacBook" price=2499.99]]: ftml
description = "Professional laptop for developers"
specs = {
    cpu = "M3",
    ram = 16,
    display = "14-inch Liquid Retina XDR",
}
[[/]]
```

Two paths to the same section:
- `#schema.product.laptop` → schema path
- `#product.laptop` → data path

## Why Use Both?

**Schema path** is for:
- Schema matching (validates properties)
- Finding all schema-validated data
- Discovering what schemas exist

```python
.filter("#schema*")                  // everything with schemas
.filter("#schema.product*")          // all product schemas and data
.filter("#schema* :ftml-schema")     // just schema definitions
```

**Data path** is for:
- Querying your actual data
- Clean hierarchy without schema prefix
- Domain-specific organization

```python
.filter("#product.laptop")           // all laptops
.filter("#product*")                 // all products
.filter("#product.laptop price>=2000") // expensive laptops
```

## When to Use This Pattern

**Use dual paths when:**
- You want schema validation AND clean data queries
- The `#schema.` prefix clutters your domain hierarchy
- You want both discoverability (via schema path) and clean queries (via data path)

**Skip dual paths when:**
- Your data hierarchy already works for queries
- The `#schema.` prefix doesn't bother you
- Simplicity matters more than flexibility

## Example: Trading System

```flextag
// Schemas
[[#schema.adapter*]]: ftml-schema
name: str
adapter_type: str
[[/]]

[[#schema.adapter.ohlcv*]]: ftml-schema
provides: [str]
supports_live: bool
[[/]]

// Data with dual paths — both header AND body are validated
[[yahoo #schema.adapter.ohlcv #adapter.yahoo name="Yahoo Finance" adapter_type="ohlcv" provides=["fetch_bars"] supports_live=false]]: ftml
description = "Free US equity data via Yahoo Finance API"
coverage = ["US equities", "ETFs", "indices"]
rate_limit = {
    requests_per_minute = 60,
    burst = 10,
}
[[/]]

[[polygon #schema.adapter.ohlcv #adapter.polygon name="Polygon.io" adapter_type="ohlcv" provides=["fetch_bars", "stream_bars"] supports_live=true]]: ftml
description = "Real-time and historical market data"
coverage = ["US equities", "options", "forex", "crypto"]
rate_limit = {
    requests_per_minute = 100,
    burst = 20,
}
[[/]]
```

Queries:
```python
// Via schema path
.filter("#schema.adapter*")              // all adapters with schema validation

// Via data path
.filter("#adapter.yahoo")                // just Yahoo adapter
.filter("#adapter* supports_live=true")  // all live adapters

// Both work for the same data
```

## Not Required

Dual paths are a pattern, not a requirement. Single path works fine:

```flextag
[[macbook #schema.product.laptop name="MacBook" price=2499.99]]: ftml
description = "Professional laptop"
[[/]]
```

Query via `#schema.product.laptop`. The `#schema.` prefix is always there, but that's fine if it doesn't bother you.
