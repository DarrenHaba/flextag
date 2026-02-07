# FlexTag Syntax Change: Field Bindings

## The Problem

With unified tags (`#tag` instead of `@path`), the `@` prefix is now available. We can repurpose it for something powerful: **binding section headers to content fields**.

Currently, there's no connection between what's in a section header and what's in the section content. You can't query based on field values inside sections.

## New Syntax (v0.4.0a1)

The `@` prefix creates a **field binding** — a link between the section header and a field in the content.

```flextag
[[#category.electronics @name @price]]: ftml
name: str = "MacBook Pro 16"
price: float = 2499.99
[[/]]
```

- `@name` in the header binds to `name:` in the content
- `@price` in the header binds to `price:` in the content

## Field-Level Queries

This enables filtering on actual data values:

```python
view.filter("#category* @price > 100")      # Products over $100
view.filter("#category* @price < 50")       # Cheap products
view.filter("#category.electronics @name")  # Get electronics names
```

Tags for hierarchy. Field bindings for data. Same query syntax for both.

## Works With Any Content Type

Field bindings work with any content type — FTML, YAML, JSON, TOML. They all parse down to dictionaries, so the binding just looks up the field in that dictionary.

```flextag
[[#config @host @port]]: yaml
host: localhost
port: 5432
[[/]]

[[#settings @theme @language]]: json
{
  "theme": "dark",
  "language": "en"
}
[[/]]

[[#database @connection]]: toml
connection = "postgres://localhost/db"
[[/]]
```

Same `@field` binding syntax. Same queries. The content format doesn't matter — it all becomes a dict.

---

## Primitives Only

Field bindings can only bind to primitive values — strings, numbers, booleans. Binding to objects or lists throws a parse error.

```flextag
// VALID - primitives
[[#product @name @price @active]]: ftml
name: str = "MacBook"
price: float = 2499.99
active: bool = true
[[/]]

// INVALID - throws parse error
[[#product @config]]: ftml
config: {
    discount: float = 0.15,
    taxable: bool = true
}
[[/]]
```

Why? Bindings exist for querying (`@price > 100`). You can't compare objects or lists. The error happens at parse time, not when you run a query.

---

## Schema Integration

Field bindings work with the schema system. In a schema, `@field` means "this field binding is required":

**Data:**
```flextag
[[#category.electronics @name @price]]: ftml
name: str = "MacBook Pro 16"
price: float = 2499.99
[[/]]
```

**Schema:**
```flextag
---schema---
[[#category+ @name @price]]: ftml
name: str
price: float
---/schema---
```

The schema says: any section matching `#category+` must have `@name` and `@price` bindings, and those fields must exist in the FTML content with the specified types.

## Examples

```flextag
[[#user.alice @email @age]]: ftml
email: str = "alice@example.com"
age: int = 32
[[/]]

[[#user.bob @email @age]]: ftml
email: str = "bob@example.com"
age: int = 28
[[/]]
```

**Queries:**
```python
view.filter("#user* @age > 30")         # Users over 30
view.filter("#user* @age >= 18 @age < 65")  # Working age users
view.filter("#user.alice @email")       # Get Alice's email
```

## Why

- **Queryable data**: Filter sections by their content, not just their tags
- **Self-documenting**: Field bindings in the header show what data the section exposes
- **Schema validation**: Ensure sections have required fields with correct types
- **Unified syntax**: Same `@field` pattern in headers, schemas, and queries

## Summary

| Prefix | Meaning | Example |
|--------|---------|---------|
| `#tag` | Category/hierarchy (exact match) | `#category.electronics` |
| `#tag+` | Immediate children | `#category+` |
| `#tag*` | All descendants | `#category*` |
| `@field` | Field binding to content | `@price` |
