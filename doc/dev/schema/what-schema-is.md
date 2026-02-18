# What FlexTag Schema Is

## Core Concept

Schema defines required fields for sections with matching tags.

## Two Schema Content Types

### `ftml-schema` — Full Validation

Validates both header properties AND FTML body content:

```flextag
[[#adapter.**]]: ftml-schema
name: str
adapter_type: str
[[/]]
```

Two separate validations occur:
1. **Header properties** — validated against the schema
2. **FTML body content** — also validated against the same schema (when content type is `ftml`)

These are independent. The header and body can have different data — both must satisfy the schema.

### `schema` — Metadata-Only Validation

Validates header properties only. Body content is ignored regardless of content type:

```flextag
// Only checks that matching sections have the right tags/params
[[#symbol.* (#nyse | #nasdaq | #arca)]]: schema
[[/]]

// With property definitions — validates header params, ignores body
[[#symbol.* name:str type:str]]: schema
[[/]]
```

Use `schema` when you want to enforce tag/parameter structure on sections that use any content type (JSON, YAML, text, etc.) — or when you only care about metadata.

## Schema Section vs Data Section

**Schema section** — defines the contract:
```flextag
[[#adapter.**]]: ftml-schema
name: str
adapter_type: str
[[/]]
```

**Data section** — must follow the contract:
```flextag
[[yahoo #adapter.ohlcv name="Yahoo Finance" adapter_type="ohlcv"]]: ftml
description = "Free US equity data via Yahoo Finance API"
coverage = ["US equities", "ETFs"]
[[/]]
```

The differences:
- Type is `ftml-schema` or `schema` for schema definitions, anything else for data
- Schema body uses FTML type definitions (`:` syntax)
- Data body uses FTML data values (`=` syntax)
- Header properties (on both) use `key=value`
- Header property definitions on schema use `key:type` (e.g., `name:str`)

## Tag Matching Syntax

Schema tags use the **same glob-style wildcard syntax as filter queries**:

| Syntax | Meaning |
|--------|---------|
| `#tag` | Exact match (default) |
| `#tag.*` | Direct children (one level) |
| `#tag.**` | All descendants (any depth) |
| `#fo*` | Character wildcard (name starts with prefix) |
| `!#tag` | Negation (must NOT have tag) |
| `(#a \| #b)` | OR group (at least one must match) |

### Exact Match (default)

```flextag
// Only matches sections with exactly #adapter tag
[[#adapter]]: ftml-schema
name: str
[[/]]

[[yahoo #adapter name="Yahoo"]]: ftml
description = "Matches — has exact #adapter tag"
[[/]]

[[yahoo #adapter.ohlcv name="Yahoo"]]: ftml
description = "Does NOT match — #adapter.ohlcv is not #adapter"
[[/]]
```

### All Descendants with `.**`

```flextag
// Matches #adapter.ohlcv, #adapter.ohlcv.yahoo, etc. (NOT #adapter itself)
[[#adapter.**]]: ftml-schema
name: str
[[/]]

[[yahoo #adapter.ohlcv name="Yahoo"]]: ftml
description = "Matches — #adapter.ohlcv is a descendant of #adapter"
[[/]]
```

### Direct Children with `.*`

```flextag
// Matches #adapter.ohlcv, #adapter.news — but NOT #adapter itself or #adapter.ohlcv.yahoo
[[#adapter.*]]: ftml-schema
adapter_type: str
[[/]]

[[yahoo #adapter.ohlcv adapter_type="ohlcv"]]: ftml
description = "Matches — one level deep"
[[/]]

[[deep #adapter.ohlcv.yahoo adapter_type="ohlcv"]]: ftml
description = "Does NOT match — two levels deep"
[[/]]
```

## Multiple Schema Tags (AND)

Multiple tags on a schema means ALL must match:

```flextag
// Section must have BOTH #adapter AND #live
[[#adapter #live]]: ftml-schema
api_key: str
rate_limit: int
[[/]]
```

## OR Groups

Use `|` with `()` to require at least one of several tags:

```flextag
// Section must have #adapter AND one of (#ohlcv | #news)
[[#adapter (#ohlcv | #news)]]: ftml-schema
name: str
provides: [str]
[[/]]
```

## Layered Schemas

You can build up requirements through multiple schemas:

```flextag
// Base — all adapters need name
[[#adapter.**]]: ftml-schema
name: str
[[/]]

// OHLCV adapters also need timeframes
[[#adapter.ohlcv.**]]: ftml-schema
timeframes: [str]
[[/]]

// A section tagged #adapter.ohlcv matches BOTH schemas
[[yahoo #adapter.ohlcv name="Yahoo" timeframes=["1d","1wk"]]]: ftml
description = "Must have name (from first schema) AND timeframes (from second schema)"
[[/]]
```

## No Optional Markers

You don't need `?` to mark optional fields. Tag presence IS the conditional logic.

- No `#live` tag? Don't need `api_key` property.
- No `#adapter.ohlcv` tag? Don't need `timeframes` property.

The tag system handles optionality naturally.

## Header vs Body

The header and body are validated separately against the same schema:

```flextag
[[yahoo #adapter name="Yahoo Finance"]]: ftml
// Header: name="Yahoo Finance" — validated
// Body below also validated when content type is ftml

name = "Yahoo Finance (detailed)"
description = "Free market data provider"
api_docs = "https://finance.yahoo.com"
[[/]]
```

Note: The header and body can have different values. Both are validated independently. Extra fields in the body (like `description`) are allowed — the schema only requires `name` to be present and correctly typed.
