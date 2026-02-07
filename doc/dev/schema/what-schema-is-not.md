# What FlexTag Schema Is Not

## Not a Document Grammar

Traditional schemas define document structure — what sections must exist, in what order, how many of each.

FlexTag schema does not do this. There's no:
- Required section ordering
- "You must have exactly 3 of these sections"
- "Section A must come before section B"

FlexTag is about filtering and composition, not rigid document structure.

## Not Strict Mode

There is no strict mode. Sections that don't match any schema are allowed.

**Why?** Because filtering makes it irrelevant.

```flextag
[[#adapter #ohlcv]]: ftml-schema
name: str
adapter_type: str
[[/]]

[[alpaca #adapter #ohlcv name="Alpaca" adapter_type="ohlcv"]]: ftml
description = "Commission-free trading API"
[[/]]

[[#notes]]: text
TODO: remember to fix that thing
[[/]]

[[#scratch]]: yaml
foo: bar
temp: 123
[[/]]
```

When you query `#adapter`, you get alpaca. The notes and scratch data don't exist to that query. They're filtered out.

**Unmatched sections don't pollute your results. They're invisible to queries that don't ask for them.**

This is the beauty of FlexTag. Strict mode would restrict flexibility for no real benefit. The "junk" in a file is someone's notes, temporary data, or work-in-progress. It doesn't interfere with anything.

## Not JSON Schema

We're not trying to validate every content type. FlexTag schema validates:
1. Header properties (always)
2. Body content (only when content type is `ftml`)

If you have YAML, JSON, or TOML sections and want body validation, use their native schema systems. FlexTag won't reinvent that wheel. (Header properties are still validated.)

## Not a Universal Validator

Schema validation is opt-in. If a section has no matching schema, it passes through unvalidated. That's fine.

You define schemas for the parts that matter — your core data structures, your interfaces, your contracts. Everything else is free-form.

## Not Inherited

Schemas don't inherit from each other. Each schema is independent.

```flextag
// These are separate, independent schemas
[[#adapter]]: ftml-schema
name: str
[[/]]

[[#adapter #ohlcv]]: ftml-schema
adapter_type: str
[[/]]
```

A section with `#adapter #ohlcv` must satisfy both schemas independently. The second schema doesn't "extend" the first — they're just two contracts that both apply.
