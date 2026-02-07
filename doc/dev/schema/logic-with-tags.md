# Logic with Tags

Schema matching uses tags to express logical conditions. There's no special syntax for AND, OR, IF-THEN — the tag system itself is the logic.

## Exact Match (Default)

A single tag on a schema means the section must **have** that exact tag:

```flextag
[[#adapter]]: ftml-schema
name: str
[[/]]
```

This checks for **presence**, not exclusivity. A section with `#adapter #ohlcv #live` still matches — it has `#adapter`. A section with only `#adapter.ohlcv` does not — that's a different tag. Extra tags on the section are fine; the schema only cares that its required tags are present.

Use `*` or `+` to match descendants (see [what-schema-is.md](what-schema-is.md) for details).

## AND

Multiple tags on one schema means all must be present:

```flextag
[[#adapter #ohlcv]]: ftml-schema
name: str
provides: [str]
[[/]]
```

Section must have `#adapter` AND `#ohlcv` to match. Each tag is still an exact match.

## OR

Create separate schemas:

```flextag
[[#adapter #ohlcv]]: ftml-schema
name: str
provides: [str]
[[/]]

[[#adapter #news]]: ftml-schema
name: str
provides: [str]
[[/]]
```

A section with `#adapter #ohlcv` matches the first.
A section with `#adapter #news` matches the second.

OR is expressed by having multiple schemas with different tag requirements.

## IF-THEN (Conditional Layering)

IF-THEN comes from layering multiple schemas — a base schema plus more specific ones:

```flextag
// All adapters must have connection_timeout
[[#adapter*]]: ftml-schema
connection_timeout: int
[[/]]

// Live adapters must ALSO have supports_live
[[#adapter.live]]: ftml-schema
supports_live: bool
[[/]]
```

This creates a conditional effect:

- **IF** `#adapter.ohlcv` → must have `connection_timeout` (base schema applies)
- **IF** `#adapter.live` → must have `connection_timeout` AND `supports_live` (both schemas apply)

The "IF-THEN" isn't a single schema doing something special — it's the **combination** of schemas creating conditional requirements. The more specific tag picks up additional rules on top of the base.

Another way to express this with flat tags:

```flextag
// Base requirements for all adapters
[[#adapter]]: ftml-schema
connection_timeout: int
[[/]]

// Extra requirements only when #live is also present
[[#adapter #live]]: ftml-schema
supports_live: bool
[[/]]
```

A section with `#adapter` only gets `connection_timeout`.
A section with `#adapter #live` gets both `connection_timeout` and `supports_live`.

Either approach works — hierarchical tags (`#adapter.live`) or flat tags (`#adapter #live`). The IF-THEN effect is the same: more tags = more schemas match = more requirements.

## NOT (Negation)

Use `!#tag` to exclude sections that have a specific tag:

```flextag
// Applies to adapters that are NOT deprecated
[[#adapter !#deprecated]]: ftml-schema
api_endpoint: str
rate_limit: int
[[/]]
```

A section with `#adapter` matches. A section with `#adapter #deprecated` does not — the `!#deprecated` excludes it.

Negation works with modifiers too:

```flextag
// Applies to all adapter descendants that are NOT in the legacy hierarchy
[[#adapter* !#adapter.legacy*]]: ftml-schema
api_version: str
[[/]]
```

## Summary

| Logic                  | How to Express                                       |
|------------------------|------------------------------------------------------|
| a AND b                | `[[#a #b]]: ftml-schema`                             |
| a OR b                 | Two schemas: `[[#a]]` and `[[#b]]`                   |
| a AND NOT b            | `[[#a !#b]]: ftml-schema`                            |
| IF a THEN require X    | Base `[[#a]]` + specific `[[#a #b]]` schemas layered |
| Base + optional extras | Layered schemas with increasing specificity          |

## What We Don't Support

- **XOR**: "must have exactly one of these tags" — would require app code

This edge case rarely comes up in practice. If it does, handle it in application code.
