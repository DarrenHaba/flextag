# FlexTag Schema Design

Documentation for the FlexTag schema system.

## Files

- [what-schema-is.md](what-schema-is.md) — Core concept and how it works
- [what-schema-is-not.md](what-schema-is-not.md) — What we explicitly don't do
- [why-no-strict-mode.md](why-no-strict-mode.md) — When to use `strict=True` vs default relaxed validation
- [naming-conventions.md](naming-conventions.md) — Tag conventions for schema discoverability
- [dual-tag-paths.md](dual-tag-paths.md) — Using multiple tags and tagged parameters together
- [logic-with-tags.md](logic-with-tags.md) — How to express AND, OR, IF-THEN with tags
- [other-markup-languages.md](other-markup-languages.md) — Why we're not supporting JSON Schema (yet)

## The Big Picture

**Two schema content types:**

- **`ftml-schema`** — validates BOTH header properties AND FTML body content
- **`schema`** — validates header properties only (body ignored, any content type)

```flextag
[[#product name="MacBook" price=2499.99]]: ftml
   ^--- Schema validates header properties

description = "Professional laptop for developers"
specs = {
    weight = "1.4 kg",
    display = "14-inch Liquid Retina XDR",
}
   ^--- ftml-schema ALSO validates FTML body content
   ^--- schema ignores body entirely
[[/]]
```

The header and body are validated independently against the same schema.

## Why `ftml-schema` and `schema`?

The section type describes **what's inside the section**.

```flextag
[[#product]]: ftml           // content is FTML data
[[#product]]: ftml-schema    // content is FTML schema (type definitions)
[[#product]]: schema         // metadata-only schema (body ignored)
```

`ftml-schema` is "FTML schema content inside a FlexTag section." `schema` is for metadata-only validation — when you only care about tags and header parameters.

## Tag Matching Syntax

Schema tags use **exact match** — no hierarchy, no wildcards. Tags are flat.

| Syntax | Meaning |
|--------|---------|
| `#tag` | Exact match (default) |
| `!#tag` | Negation (must NOT have tag) |
| `(#a \| #b)` | OR group (at least one must match) |
| `key=#value` | Parameter with tagged value |
| `key=` | Parameter key must exist |

```flextag
// Exact — only validates sections tagged exactly #adapter
[[#adapter]]: ftml-schema
name: str
[[/]]

// With tagged parameter constraint
[[#adapter type=#ohlcv]]: ftml-schema
timeframes: [str]
[[/]]
```

## Quick Summary

**One sentence:** Schema defines required fields for sections with matching tags — `ftml-schema` validates header + body, `schema` validates header only.

**Key insight:** Schema tags use exact match. Use multiple flat tags and tagged parameters for structured matching.

**Not strict by default:** Unmatched sections are allowed. For structured data files, use `strict=True` to require every section to match at least one schema.

**No optional markers:** Tag presence IS the conditional logic. If you don't have `#discounted` tag, you don't need `discount` property.

## Example

```flextag
// Schema — all adapters must have name and adapter_type
[[#adapter]]: ftml-schema
name: str
adapter_type: str
[[/]]

// Schema — ohlcv adapters also need timeframes
[[#adapter type=#ohlcv]]: ftml-schema
timeframes: [str]
supports_live: bool
[[/]]

// Data — matches BOTH schemas (#adapter and #adapter type=#ohlcv)
[[#adapter type=#ohlcv source=#yahoo name="Yahoo Finance" adapter_type="ohlcv" timeframes=["1d","1wk"] supports_live=false]]: ftml
description = "Free market data provider"
coverage = ["US equities", "ETFs", "indices"]
[[/]]

// Data — matches only the first schema (#adapter)
[[#adapter type=#news source=#rss name="RSS Feed" adapter_type="news"]]: ftml
description = "Generic RSS news feed adapter"
[[/]]
```

Query examples:
```python
.filter("#adapter")                   // all adapters
.filter("type=#ohlcv")               // all OHLCV adapters
.filter("supports_live=true")        // property filter
.filter(":ftml-schema")              // all schema definitions
.filter("#adapter").values("type")   // → ["#ohlcv", "#news"]
```
