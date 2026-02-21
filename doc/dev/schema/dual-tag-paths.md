# Multiple Tags

## The Pattern

A section can have multiple tags for different purposes:

```flextag
[[#product #electronics #featured name="MacBook" price=2499.99]]: ftml
description = "Professional laptop for developers"
specs = {
    cpu = "M3",
    ram = 16,
    display = "14-inch Liquid Retina XDR",
}
[[/]]
```

Multiple tags on the same section:
- `#product` → matches the product schema
- `#electronics` → matches the electronics-specific schema
- `#featured` → matches the featured items schema

## Why Use Multiple Tags?

**Different schemas** can apply to different aspects:

```flextag
// Base schema — all products
[[#product]]: ftml-schema
name: str
price: float
[[/]]

// Category-specific schema
[[#product #electronics]]: ftml-schema
warranty: str
brand: str
[[/]]

// Display schema
[[#featured]]: ftml-schema
display_order: int
[[/]]
```

**Different queries** target different concerns:

```python
.filter("#product")                  // all products
.filter("#product #electronics")     // electronics only
.filter("#featured")                 // all featured items
.filter("#featured price>=2000")     // expensive featured items
```

## Tagged Parameters for Structure

Use tagged parameters to add structured metadata without extra tags:

```flextag
[[#adapter type=#ohlcv source=#yahoo name="Yahoo Finance" adapter_type="ohlcv"]]: ftml
description = "Free US equity data via Yahoo Finance API"
coverage = ["US equities", "ETFs", "indices"]
[[/]]

[[#adapter type=#ohlcv source=#polygon name="Polygon.io" adapter_type="ohlcv"]]: ftml
description = "Real-time and historical market data"
coverage = ["US equities", "options", "forex", "crypto"]
[[/]]
```

Queries:
```python
// By tag
.filter("#adapter")                      // all adapters

// By tagged parameter
.filter("type=#ohlcv")                  // all OHLCV adapters
.filter("source=#yahoo")               // just Yahoo

// Discover available values
view.filter("#adapter").values("type")  // → ["#ohlcv", "#news"]
view.filter("#adapter").values("source") // → ["#yahoo", "#polygon"]
```

## Not Required

Multiple tags are a pattern, not a requirement. A single tag works fine:

```flextag
[[#product name="MacBook" price=2499.99]]: ftml
description = "Professional laptop"
[[/]]
```

Query via `#product`. Add more tags when you need more specific schema matching or filtering.
