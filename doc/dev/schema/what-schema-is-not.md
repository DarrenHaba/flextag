# What FlexTag Schema Is Not

## Not a Document Grammar

Traditional schemas define document structure — what sections must exist, in what order, how many of each.

FlexTag schema does not do this. There's no:
- Required section ordering
- "You must have exactly 3 of these sections"
- "Section A must come before section B"

FlexTag is about filtering and composition, not rigid document structure.

## Not Strict by Default

By default, sections that don't match any schema are allowed. Filtering makes it irrelevant — unmatched sections are invisible to queries that don't ask for them.

For structured data files where every section must be validated, use `strict=True`:

```python
view = flextag.load(path="symbols.ft", validate=True, strict=True)
```

See `why-no-strict-mode.md` for details on when to use each approach.

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
