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

**Two separate validations occur:**
1. **Header properties** (e.g., `name="Coffee Mug"`) — always validated
2. **FTML body content** — validated when content type is `ftml`

Header and body are validated independently. They can have different values. Extra fields in the body are allowed — the schema only requires its defined fields to be present and correctly typed.

## Tag Matching Syntax

Schema tags use the same syntax as filter queries:

| Syntax  | Meaning                        |
|---------|--------------------------------|
| `#tag`  | Must have this tag (default)   |
| `#tag*` | Self + all descendants         |
| `#tag+` | Immediate children only        |
| `!#tag` | Must NOT have this tag         |

### `#tag` — Must Have Tag

```flextag
[[#product]]: ftml-schema
name: str
[[/]]

// Matches — has #product
[[#product name="Coffee Mug"]]: ftml
description = "Ceramic mug"
[[/]]

// Does NOT match — #product.electronics is a different tag than #product
[[#product.electronics name="Keyboard"]]: ftml
description = "Not validated by this schema"
[[/]]

// Matches — has #product (extra tags are fine)
[[#product #featured #sale name="Coffee Mug"]]: ftml
description = "Schema checks for presence, not exclusivity"
[[/]]
```

### `#tag*` — Self + All Descendants

```flextag
// Matches #product, #product.electronics, #product.electronics.keyboards, etc.
[[#product*]]: ftml-schema
name: str
[[/]]
```

### `#tag+` — Immediate Children Only

```flextag
// Matches #product.electronics, #product.clothing — but NOT #product itself or #product.electronics.keyboards
[[#product+]]: ftml-schema
category: str
[[/]]
```

### `!#tag` — Negation

```flextag
// Matches sections with #product that do NOT have #clearance
[[#product !#clearance]]: ftml-schema
warranty: str
[[/]]
```

Negation works with modifiers too:

```flextag
[[#product* !#product.discontinued*]]: ftml-schema
in_stock: bool
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

Separate schema sections:

```flextag
[[#product #featured]]: ftml-schema
name: str
display_order: int
[[/]]

[[#product #sale]]: ftml-schema
name: str
display_order: int
[[/]]
```

A section with `#product #featured` matches the first. A section with `#product #sale` matches the second.

### NOT

See `!#tag` in [Tag Matching Syntax](#tag--negation) above.

### IF-THEN (Conditional Layering)

Layer multiple schemas — a base schema plus more specific ones:

```flextag
// All products must have name and price
[[#product*]]: ftml-schema
name: str
price: float
[[/]]

// Electronics also need warranty
[[#product.electronics]]: ftml-schema
warranty: str
[[/]]
```

- `#product.clothing` gets `name` and `price` (base schema applies)
- `#product.electronics` gets `name`, `price`, AND `warranty` (both schemas apply)

The same effect with flat tags:

```flextag
[[#product]]: ftml-schema
name: str
price: float
[[/]]

[[#product #electronics]]: ftml-schema
warranty: str
[[/]]
```

A section with `#product` only gets `name` and `price`. A section with `#product #electronics` gets all three.

### Summary

| Logic                  | How to Express                                       |
|------------------------|------------------------------------------------------|
| a AND b                | `[[#a #b]]: ftml-schema`                             |
| a OR b                 | Two schemas: `[[#a]]` and `[[#b]]`                   |
| a AND NOT b            | `[[#a !#b]]: ftml-schema`                            |
| IF a THEN require X    | Base `[[#a]]` + specific `[[#a #b]]` schemas layered |

XOR ("must have exactly one of these tags") is not supported. Handle in application code.

## Validation Details

- **Opt-in** — sections without a matching schema pass through unvalidated
- **No strict mode** — unmatched sections are allowed; filtering makes them irrelevant
- **Multiple schemas can match** — a section with `#product #electronics` could match both a `[[#product*]]` schema and a `[[#product #electronics]]` schema; all apply independently
- **Schemas don't inherit from each other** — each is an independent contract
- **No optional markers** — tag presence IS the conditional; no `#electronics` tag means no `warranty` requirement

## Header Parameters vs Body Content

Header parameters are for quick filtering. Body content holds the full data.

```flextag
[[#product.electronics name="Wireless Keyboard" price=79.99]]: ftml
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
electronics = view.filter("#product.electronics*")
for section in electronics:
    data = section.content  // parsed FTML dict
    if data["specs"]["weight"] == "450g":
        ...
```

FlexTag is not a database. Tags and header parameters handle fast filtering. For deeper queries on body content, work with the parsed data directly.

## Naming Conventions

### The `#schema.` Prefix

Optional convention for discoverability. Prefix schema-related tags with `#schema.`:

```flextag
[[#schema.product*]]: ftml-schema
name: str
price: float
[[/]]

[[#schema.product name="Coffee Mug" price=12.99]]: ftml
description = "Ceramic mug"
[[/]]
```

Makes querying easy:

```python
view.filter("#schema* :ftml-schema")   // all schema definitions
view.filter("#schema* :ftml")          // all schema-validated data
view.filter("#schema*")               // everything schema-related
```

Not enforced — just a recommended convention. Skip it when adding schemas to existing data.

### Dual Tag Paths

Use both a schema path and a data path on the same section:

```flextag
[[#schema.product.electronics #product.electronics name="Keyboard" price=79.99]]: ftml
description = "Mechanical keyboard"
[[/]]
```

- `#schema.product.electronics` for schema matching and discoverability
- `#product.electronics` for clean data queries

## Full Example

```flextag
// Schema — all products must have name and price
[[#product*]]: ftml-schema
name: str
price: float
[[/]]

// Schema — electronics also need warranty
[[#product.electronics*]]: ftml-schema
warranty: str
brand: str
[[/]]

// Schema — non-clearance products must have return_policy
[[#product* !#clearance]]: ftml-schema
return_policy: str
[[/]]

// Data — matches first two schemas
[[#product.electronics name="Wireless Keyboard" price=79.99 warranty="2 years" brand="Logitech" return_policy="30 days"]]: ftml
description = "Bluetooth mechanical keyboard"
features = ["backlit", "rechargeable", "multi-device"]
specs = {
    layout = "full-size",
    switches = "brown",
    battery = "20 hours",
}
[[/]]

// Data — matches first schema only
[[#product.clothing name="T-Shirt" price=19.99 return_policy="14 days"]]: ftml
description = "100% cotton crew neck"
sizes = ["S", "M", "L", "XL"]
[[/]]

// Data — clearance item, so return_policy schema does NOT apply
[[#product.electronics #clearance name="Old Mouse" price=9.99 warranty="none" brand="Generic"]]: ftml
description = "Last season model"
[[/]]

// Notes — no schema matches, no validation, totally fine
[[#notes]]: text
TODO: add more products to the catalog
[[/]]
```

Queries:
```python
view.filter("#product*")                 // all products
view.filter("#product.electronics*")     // electronics only
view.filter("#product* !#clearance")     // non-clearance products
view.filter("price>50")                  // expensive products
view.filter(":ftml-schema")             // all schema definitions
```
