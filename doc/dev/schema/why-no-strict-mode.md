# Strict Mode

## Two Approaches

FlexTag supports both relaxed and strict validation:

```python
// Default — unmatched sections pass through
view = flextag.load(path="config.ft", validate=True)

// Strict — every section must match at least one schema
view = flextag.load(path="symbols.ft", validate=True, strict=True)
```

## When to Use `strict=False` (Default)

For files with mixed content — config, notes, scratch data, work-in-progress:

```flextag
// Schema: adapters must have name and type
[[#adapter.**]]: ftml-schema
name: str
adapter_type: str
[[/]]

// Valid adapter
[[yahoo #adapter.ohlcv name="Yahoo Finance" adapter_type="ohlcv"]]: ftml
description = "Free US equity data"
[[/]]

// Random notes — no schema matches, no validation, totally fine
[[#notes]]: text
Remember to add more adapters later.
[[/]]

// Scratch data — no schema matches
[[#temp-config]]: yaml
debug: true
test_mode: true
[[/]]
```

```python
view.filter("#adapter.**")
// Returns: yahoo only. Notes and temp-config are invisible.
```

The notes and scratch data exist in the file, but they're invisible to queries that don't ask for them. No strict mode needed.

## When to Use `strict=True`

For structured data files where every section must be validated:

```flextag
// Every symbol child must have an exchange tag
[[#symbol.* (#nyse | #nasdaq | #arca | #bats | #amex | #otc)]]: schema
[[/]]

// Every symbol child must have these fields
[[#symbol.*]]: ftml-schema
name: str
type: str
list_date: str
[[/]]

// 13,000 symbol sections...
[[#symbol.aapl #nasdaq name="Apple Inc." type="CS" list_date="1980-12-12"]]: ftml
sic_description = "ELECTRONIC COMPUTERS"
[[/]]
```

```python
// Catches any malformed section on load
view = flextag.load(path="symbols.ft", validate=True, strict=True)
```

A symbol missing its exchange tag or `name` field raises `SchemaValidationError` immediately.

## What Gets Skipped

Strict mode skips these section types — they don't need to match a schema:
- `ftml-schema` — schema definitions themselves
- `schema` — metadata-only schema definitions
- `file-metadata` — file-level metadata
