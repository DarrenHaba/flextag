# FlexTag Schema

Schema defines required fields for sections with matching tags.

## How It Works

A schema section defines the contract. A data section follows it.

```flextag
// Schema — defines required fields
[[#product]]: ftml-schema
name: str
price: float
[[/]]

// Data — validated against the schema
[[#product name="Coffee Mug" price=12.99]]: ftml
description = "Ceramic mug, 12oz"
color = "blue"
[[/]]
```

The section type `ftml-schema` means "this section contains FTML schema definitions." Schema bodies use `:` for type definitions. Data bodies use `=` for values.

**Two separate validations occur with `ftml-schema`:**
1. **Header properties** (e.g., `name="Coffee Mug"`) — always validated
2. **FTML body content** — validated when content type is `ftml`

Header and body are validated independently. They can have different values. Extra fields in the body are allowed — the schema only requires its defined fields to be present and correctly typed.

### `schema` — Metadata-Only

The `schema` content type validates header properties only. Body content is ignored:

```flextag
// Only checks tags and header params — body is irrelevant
[[#symbol exchange=(#nyse | #nasdaq | #arca)]]: schema
[[/]]

// With header property definitions
[[#symbol name:str type:str]]: schema
[[/]]
```

Use `schema` when you want to enforce tag/parameter structure on sections with any content type (JSON, YAML, text, etc.).

## Tag Matching Syntax

Schema tags use exact match. Tags are flat — no hierarchy, no wildcards.

| Syntax  | Meaning                        |
|---------|--------------------------------|
| `#tag`  | Must have this tag (exact match) |
| `!#tag` | Must NOT have this tag         |
| `(#a \| #b)` | OR group (at least one must match) |
| `key=#value` | Parameter with tagged value |
| `key=` | Parameter key must exist |

### `#tag` — Must Have Tag

```flextag
[[#product]]: ftml-schema
name: str
[[/]]

// Matches — has #product
[[#product name="Coffee Mug"]]: ftml
description = "Ceramic mug"
[[/]]

// Matches — has #product (extra tags are fine)
[[#product #featured #sale name="Coffee Mug"]]: ftml
description = "Schema checks for presence, not exclusivity"
[[/]]
```

### `!#tag` — Negation

```flextag
// Matches sections with #product that do NOT have #clearance
[[#product !#clearance]]: ftml-schema
warranty: str
[[/]]
```

### Tagged Parameters in Schemas

Schema headers can use tagged parameter values to constrain which sections match:

```flextag
// Only matches sections where exchange is one of the listed values
[[exchange=(#nyse | #nasdaq | #arca)]]: schema
[[/]]

// Matches sections that have an exchange parameter (any value)
[[exchange=]]: schema
[[/]]
```

## Conditional Logic

### AND

Multiple tags on one schema — all must be present:

```flextag
[[#product #featured]]: ftml-schema
name: str
display_order: int
[[/]]
```

Section must have `#product` AND `#featured` to match.

### OR

Use `|` with `()` grouping:

```flextag
// Section must have #product AND one of (#featured | #sale)
[[#product (#featured | #sale)]]: ftml-schema
name: str
display_order: int
[[/]]
```

Or use `|` in filter queries:

```python
view.filter("#featured | #sale")
```

### NOT

See `!#tag` in [Tag Matching Syntax](#tag--negation) above.

### IF-THEN (Conditional Layering)

Layer multiple schemas — a base schema plus more specific ones:

```flextag
// All products must have name and price
[[#product]]: ftml-schema
name: str
price: float
[[/]]

// Electronics also need warranty
[[#product #electronics]]: ftml-schema
warranty: str
[[/]]
```

- A section with `#product` only gets `name` and `price` (base schema applies)
- A section with `#product #electronics` gets `name`, `price`, AND `warranty` (both schemas apply)

### Summary

| Logic                  | How to Express                                       |
|------------------------|------------------------------------------------------|
| a AND b                | `[[#a #b]]: ftml-schema`                             |
| a OR b                 | `[[#a (#x \| #y)]]: ftml-schema` or `view.filter("#a \| #b")` |
| a AND NOT b            | `[[#a !#b]]: ftml-schema`                            |
| IF a THEN require X    | Base `[[#a]]` + specific `[[#a #b]]` schemas layered |

XOR ("must have exactly one of these tags") is not supported. Handle in application code.

## Validation Details

- **Opt-in by default** — sections without a matching schema pass through unvalidated
- **Strict mode available** — `strict=True` requires every section to match at least one schema
- **Multiple schemas can match** — a section with `#product #electronics` could match both a `[[#product]]` schema and a `[[#product #electronics]]` schema; all apply independently
- **Schemas don't inherit from each other** — each is an independent contract
- **No optional markers** — tag presence IS the conditional; no `#electronics` tag means no `warranty` requirement

## Strict Mode

By default, unmatched sections are allowed. For structured data files, use `strict=True`:

```python
// Default — unmatched sections pass through
view = flextag.load(path="config.ft", validate=True)

// Strict — every section must match at least one schema
view = flextag.load(path="symbols.ft", validate=True, strict=True)
```

Strict mode skips `ftml-schema`, `schema`, and `file-metadata` sections — they don't need to match a schema.

## Parameter Constraints in Schema Headers

Schema headers support property definitions with FTML constraint syntax:

```flextag
[[#symbol name:str type:str]]: schema
[[/]]
```

These are merged with body property definitions. Use this for compact schemas where all definitions fit on one line.

## Header Parameters vs Body Content

Header parameters are for quick filtering. Body content holds the full data.

```flextag
[[#product #electronics name="Wireless Keyboard" price=79.99]]: ftml
description = "Bluetooth mechanical keyboard"
features = ["backlit", "rechargeable", "multi-device"]
specs = {
    weight = "450g",
    switches = "brown",
    battery = "20 hours",
}
[[/]]
```

- `name` and `price` are in the header — filterable with `.filter("price>50")`
- `description`, `features`, `specs` are in the body — richer data that doesn't need to be filtered

Sometimes header and body data overlaps. That's OK — put the fields you filter on in the header, and keep the full data in the body.

If you need to search body content (e.g., find products where `specs.weight = "450g"`), filter by tags first to narrow down to a small set, then parse and search the body data in your application code:

```python
electronics = view.filter("#product #electronics")
for section in electronics:
    data = section.content  // parsed FTML dict
    if data["specs"]["weight"] == "450g":
        ...
```

FlexTag is not a database. Tags and header parameters handle fast filtering. For deeper queries on body content, work with the parsed data directly.

## Tagged Parameter Queries

Tagged parameters (values prefixed with `#`) are searchable as tags:

```flextag
[[#product category=#electronics name="Wireless Keyboard" price=79.99]]: ftml
description = "Bluetooth mechanical keyboard"
[[/]]

[[#product category=#clothing name="T-Shirt" price=19.99]]: ftml
description = "100% cotton crew neck"
[[/]]
```

```python
// Search by tag — finds #electronics in any tag or parameter value
view.filter("#electronics")

// Search by key=value — explicit parameter match
view.filter("category=#electronics")

// Key-exists check — has a category parameter (any value)
view.filter("category=")

// Get unique values for cascading dropdowns
view.filter("#product").values("category")
// → ["#electronics", "#clothing"]
```

## Full Example

```flextag
// Schema — all products must have name and price
[[#product]]: ftml-schema
name: str
price: float
[[/]]

// Schema — electronics also need warranty
[[#product #electronics]]: ftml-schema
warranty: str
brand: str
[[/]]

// Schema — non-clearance products must have return_policy
[[#product !#clearance]]: ftml-schema
return_policy: str
[[/]]

// Data — matches first two schemas
[[#product #electronics name="Wireless Keyboard" price=79.99 warranty="2 years" brand="Logitech" return_policy="30 days"]]: ftml
description = "Bluetooth mechanical keyboard"
features = ["backlit", "rechargeable", "multi-device"]
specs = {
    layout = "full-size",
    switches = "brown",
    battery = "20 hours",
}
[[/]]

// Data — matches first schema only
[[#product #clothing name="T-Shirt" price=19.99 return_policy="14 days"]]: ftml
description = "100% cotton crew neck"
sizes = ["S", "M", "L", "XL"]
[[/]]

// Data — clearance item, so return_policy schema does NOT apply
[[#product #electronics #clearance name="Old Mouse" price=9.99 warranty="none" brand="Generic"]]: ftml
description = "Last season model"
[[/]]

// Notes — no schema matches, no validation, totally fine
[[#notes]]: text
TODO: add more products to the catalog
[[/]]
```

Queries:
```python
view.filter("#product")                     // all products
view.filter("#product #electronics")        // electronics only
view.filter("#product !#clearance")         // non-clearance products
view.filter("price>50")                     // expensive products
view.filter(":ftml-schema")                 // all schema definitions
```
