# FlexTag Schema Refactor

## The Problem

The current schema system tries to do too much:
- Define what sections must exist
- Define the order of sections
- Define how many of each section (?, +, *, exactly one)
- Validate content inside sections

This makes it complex, confusing, and honestly... nobody uses it.

## The New Approach

Strip it down. Schema validates **header properties AND FTML body content**.

```flextag
[[#schema.product]]: ftml-schema
name: str
price: float
[[/]]

[[#schema.product name="MacBook" price=2499.99]]: ftml
name = "MacBook"
price = 2499.99
[[/]]
```

Two separate validations:
- **Header properties** = always validated against the schema
- **FTML body content** = also validated (when content type is `ftml`)

## How Matching Works

A schema applies if the data section's tags **contain** the schema's tags.

```flextag
[[#schema.product]]: ftml-schema
name: str
price: float
[[/]]

// This matches — has #schema.product
[[#schema.product #laptop name="MacBook" price=2499.99]]: ftml
...
[[/]]
```

Extra tags don't matter. The schema fires if its tags are present.

## Nested Tag Inheritance

Nested tags inherit from their parents:

```flextag
[[#schema.product]]: ftml-schema
name: str
price: float
[[/]]

[[#schema.product.laptop]]: ftml-schema
cpu: str
ram: int
[[/]]
```

A section with `#schema.product.laptop` matches BOTH schemas:

```flextag
[[#schema.product.laptop name="MacBook" price=2499.99 cpu="M3" ram=16]]: ftml
...
[[/]]
```

Must have: `name`, `price` (from parent) + `cpu`, `ram` (from laptop).

## Multiple Schemas Can Match

```flextag
[[#schema.product]]: ftml-schema
name: str
price: float
[[/]]

[[#schema.product.laptop]]: ftml-schema
cpu: str
ram: int
[[/]]

[[#schema.product.discounted]]: ftml-schema
discount: float
original_price: float
[[/]]
```

A discounted laptop:

```flextag
[[#schema.product.laptop #schema.product.discounted name="MacBook" price=1999.99 cpu="M3" ram=16 discount=0.20 original_price=2499.99]]: ftml
...
[[/]]
```

Matches all three. Must satisfy all contracts.

## No Optional Markers

You don't need `?` for optional fields. Tag presence IS the conditional.

- No `#discounted` tag? Don't need `discount` property.
- No `#laptop` tag? Don't need `cpu` property.

## Sections With No Matching Schema

Allowed. They're just not validated.

```flextag
[[#notes]]: text
Random notes here, no schema applies
[[/]]
```

Schema is opt-in validation, not a straitjacket.

## Dual Tag Paths

A section can have multiple tag hierarchies:

```flextag
[[#schema.product.laptop #product.laptop name="MacBook" price=2499.99 cpu="M3" ram=16]]: ftml
...
[[/]]
```

- `#schema.product.laptop` → schema path (for schema matching, discoverability)
- `#product.laptop` → data path (for querying products)

Same section, findable via either hierarchy. This is a feature.

## Query Examples

```python
.filter("#schema.product")           # all products (via schema path)
.filter("#product.laptop")           # all laptops (via data path)
.filter("#schema.product.laptop")    # laptops with schema validation
.filter(":ftml-schema")              # all schema definitions
.filter("price>=2000")               # property filter
```

## Summary

| Old Schema | New Schema |
|------------|------------|
| Document grammar (ordering, counts) | Pattern matching only |
| Complex repetition symbols (?, +, *) | Tag presence = conditional |
| Strict structure enforcement | Flexible, opt-in validation |
| Complex body validation | Validates header + FTML body |
| Confusing | Simple |

## Example: Product Catalog

```flextag
// Schemas
[[#schema.product]]: ftml-schema
name: str
price: float
[[/]]

[[#schema.product.laptop]]: ftml-schema
cpu: str
ram: int
[[/]]

[[#schema.product.discounted]]: ftml-schema
discount: float
original_price: float
[[/]]

// Data - header AND body are validated
[[#schema.product.laptop #product.laptop name="MacBook Pro" price=2499.99 cpu="M3" ram=16]]: ftml
name = "MacBook Pro"
price = 2499.99
cpu = "M3"
ram = 16
[[/]]

[[#schema.product #product.mouse name="Magic Mouse" price=99.00]]: ftml
name = "Magic Mouse"
price = 99.00
[[/]]

[[#schema.product.laptop #schema.product.discounted #product.laptop #sale name="MacBook Air" price=899.99 cpu="M2" ram=8 discount=0.10 original_price=999.99]]: ftml
name = "MacBook Air"
price = 899.99
cpu = "M2"
ram = 8
discount = 0.10
original_price = 999.99
[[/]]
```
