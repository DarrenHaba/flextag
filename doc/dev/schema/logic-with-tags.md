# Logic with Tags

Schema matching uses tags to express logical conditions. There's no special syntax for AND, NOT, IF-THEN — the tag system itself is the logic. OR uses `|` with `()` grouping.

## Exact Match (Default)

A single tag on a schema means the section must **have** that exact tag:

```flextag
[[#adapter]]: ftml-schema
name: str
[[/]]
```

This checks for **presence**, not exclusivity. A section with `#adapter #ohlcv #live` still matches — it has `#adapter`. Extra tags on the section are fine; the schema only cares that its required tags are present.

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

Use `|` with `()` grouping in a single schema:

```flextag
// Section must have #adapter AND one of (#ohlcv | #news)
[[#adapter (#ohlcv | #news)]]: ftml-schema
name: str
provides: [str]
[[/]]
```

A section with `#adapter #ohlcv` matches. A section with `#adapter #news` also matches. A section with `#adapter #websocket` does not.

In filter queries, `|` works as a top-level OR:

```python
view.filter("#ohlcv | #news")    // sections with either tag
```

## IF-THEN (Conditional Layering)

IF-THEN comes from layering multiple schemas — a base schema plus more specific ones:

```flextag
// All adapters must have connection_timeout
[[#adapter]]: ftml-schema
connection_timeout: int
[[/]]

// Live adapters must ALSO have supports_live
[[#adapter #live]]: ftml-schema
supports_live: bool
[[/]]
```

This creates a conditional effect:

- **IF** `#adapter` → must have `connection_timeout` (base schema applies)
- **IF** `#adapter #live` → must have `connection_timeout` AND `supports_live` (both schemas apply)

The "IF-THEN" isn't a single schema doing something special — it's the **combination** of schemas creating conditional requirements. The more specific tag picks up additional rules on top of the base.

Tagged parameters work the same way:

```flextag
// Base requirements for all adapters
[[#adapter]]: ftml-schema
name: str
[[/]]

// Extra requirements when type is ohlcv
[[#adapter type=#ohlcv]]: ftml-schema
timeframes: [str]
[[/]]
```

A section with `#adapter` only gets `name`.
A section with `#adapter type=#ohlcv` gets both `name` and `timeframes`.

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

## Summary

| Logic                  | How to Express                                       |
|------------------------|------------------------------------------------------|
| a AND b                | `[[#a #b]]: ftml-schema`                             |
| a OR b                 | `[[#a (#x \| #y)]]: ftml-schema` or `view.filter("#a \| #b")` |
| a AND NOT b            | `[[#a !#b]]: ftml-schema`                            |
| IF a THEN require X    | Base `[[#a]]` + specific `[[#a #b]]` schemas layered |
| Base + optional extras | Layered schemas with increasing specificity          |

## What We Don't Support

- **XOR**: "must have exactly one of these tags" — would require app code

This edge case rarely comes up in practice. If it does, handle it in application code.
