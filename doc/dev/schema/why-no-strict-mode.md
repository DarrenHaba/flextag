# Why No Strict Mode

## The Question

"What if we want to reject sections that don't match any schema?"

## The Answer

You don't need to. Filtering handles it.

## Example

```flextag
// Schema: adapters must have name and type
[[#adapter*]]: ftml-schema
name: str
adapter_type: str
[[/]]

// Valid adapter
[[yahoo #adapter.ohlcv name="Yahoo Finance" adapter_type="ohlcv"]]: ftml
description = "Free US equity data"
coverage = ["US equities", "ETFs", "indices"]
[[/]]

// Another valid adapter
[[polygon #adapter.ohlcv name="Polygon.io" adapter_type="ohlcv"]]: ftml
description = "Real-time and historical market data"
coverage = ["US equities", "options", "crypto"]
[[/]]

// Random notes — no schema matches
[[#notes]]: text
Remember to add more adapters later.
This is just a reminder for myself.
[[/]]

// Scratch data — no schema matches
[[#temp-config]]: yaml
debug: true
test_mode: true
[[/]]
```

## Querying

```python
// Get all adapters
view.filter("#adapter*")
// Returns: yahoo, polygon
// Notes and temp-config are not in results

// Get OHLCV adapters
view.filter("#adapter.ohlcv*")
// Returns: yahoo, polygon

// Get all sections (no filter)
view.sections
// Returns: all sections including notes and temp-config
```

## The Point

The notes and scratch data exist in the file, but they're invisible to queries that don't ask for them.

**Strict mode would:**
- Reject the file because `[[#notes]]` doesn't match a schema
- Force you to define schemas for everything, even throwaway notes
- Remove flexibility for no practical benefit

**Without strict mode:**
- Valid adapters are validated
- Everything else is allowed but unvalidated
- Queries return exactly what you ask for

## Real World

Developers put random stuff in files:
- Notes and TODOs
- Temporary test data
- Work-in-progress sections
- Commented-out alternatives

This is normal. This is how real projects work. Strict mode fights against this reality instead of embracing it.

FlexTag's design — tags + filtering — already handles the "junk" problem. You don't need strict mode to police the file. You just query what you want.
