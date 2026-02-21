# Goal: Tag Chains (Replace Dot Hierarchy and Wildcards)

## Background

FlexTag currently uses dot-separated hierarchy for nested tags (`#exchange.nyse.aapl`) with glob-style wildcards (`*`, `**`) for querying children and descendants. This system works but has a fundamental usability problem: users expect to search for a leaf tag like `#aapl` and find it, but they can't — the dot creates an opaque, atomic namespace that requires the full path `#exchange.nyse.aapl`.

The workaround is duplicating tags (`[[#exchange.nyse.aapl #aapl]]`), which is tedious and error-prone.

## Core Design Principle

FlexTag's syntax is designed so that **what you write in `[[...]]` is what you search with in `.filter()`**. The section header IS the search query. Any solution must preserve this symmetry.

## Problem

1. `#exchange.nyse.aapl` is an atomic tag — `.filter("#aapl")` returns nothing
2. Users repeatedly expect flat searches to work and are confused when they don't
3. The primary use case driving this: populating UI dropdowns and autocomplete from tag hierarchies. A dropdown labeled "Exchange" should list `nyse`, `nasdaq`. Once the user selects `nyse`, they see `aapl`, `goog`. But if the user types `aapl` in a search box, it should also find the section.
4. Wildcards (`*`, `**`) add cognitive overhead — users forget which is which, and the distinction between character wildcards and hierarchy wildcards is non-obvious

## Solution: Tag Chains

Replace dot hierarchy with `#`-chained tags. The `#` symbol already means "tag" — when tags are written adjacent without spaces, they form a chain where **every segment is independently searchable**.

### Syntax

```flextag
[[#exchange#nyse#aapl]]
[[#exchange#nyse#goog]]
[[#exchange#nasdaq#msft]]
```

### Storage

The tag is stored **exactly as written**: `#exchange#nyse#aapl`. No hidden expansion, no internal duplication. What the user wrote is what exists on `section.tags`.

### Matching

The matching logic in `_match_pattern()` treats `#` as a segment boundary within a chained tag. Any individual segment or contiguous sub-chain is a valid match target:

- `.filter("#aapl")` — matches (segment match)
- `.filter("#nyse")` — matches (segment match)
- `.filter("#exchange")` — matches (segment match)
- `.filter("#exchange#nyse")` — matches (contiguous sub-chain)
- `.filter("#nyse#aapl")` — matches (contiguous sub-chain)
- `.filter("#exchange#nyse#aapl")` — matches (exact)

### Trailing `#` — Direct Children Only

A trailing `#` means "this segment must be followed by exactly one more segment and then the chain ends." This replaces the old `.*` (one-level) wildcard.

```
#adapter      → everything with adapter as a segment (any depth)
#adapter#     → only chains where adapter is followed by exactly one more segment
```

Given these sections:
```flextag
[[#adapter#ohlcv#yahoo]]
[[#adapter#ohlcv]]
[[#adapter#news]]
```

- `.filter("#adapter")` → all three
- `.filter("#adapter#")` → `#adapter#ohlcv` and `#adapter#news` only (NOT `#adapter#ohlcv#yahoo`)

This is critical for **schema matching** — a schema with `[[#adapter#]]` applies to direct children of adapter but not deeper descendants. And for **cascading dropdowns** — `#adapter#` gives you just the first level.

### Inline OR Groups

OR groups can be embedded directly inside a chain using parentheses with bare names (no `#` prefix inside the group since you're already in a chain context):

```flextag
[[#symbol#(nyse|nasdaq|arca)#aapl]]: schema
```

This matches any section where:
1. `#symbol` is a segment, AND
2. The next segment is one of `nyse`, `nasdaq`, or `arca`, AND
3. The next segment after that is `aapl`

Spaces inside parentheses are allowed for readability but not required:

```flextag
[[#symbol#(nyse | nasdaq | arca)]]: schema    ← valid, readable
[[#symbol#(nyse|nasdaq|arca)]]: schema        ← valid, compact
```

Real-world schema example — validating that every symbol has a recognized exchange:

```flextag
[[#symbol#(nyse|nasdaq|arca|bats|amex|otc)#]]: schema
[[/]]
```

This says: any chain starting with `#symbol`, then one of these exchanges, then exactly one more segment (the ticker). Sections like `#symbol#nyse#aapl` match. Sections like `#symbol#unknown#aapl` do not.

### What This Replaces

| Old (dot hierarchy + wildcards) | New (tag chains) | Notes |
|---|---|---|
| `#exchange.nyse.aapl` | `#exchange#nyse#aapl` | Every segment independently searchable |
| `.filter("#exchange.*")` | `.filter("#exchange#")` | Trailing `#` = direct children only |
| `.filter("#exchange.**")` | `.filter("#exchange")` | Segment match = all depths by default |
| `.filter("#exchange.nas*")` | autocomplete at app layer | See below |
| `#fo*` (character wildcard) | removed — app layer concern | See below |

### Wildcards: Removed

Wildcards (`*`, `**`) are no longer needed in the query syntax:

- **All descendants** (`.**`) — replaced by segment matching. `.filter("#exchange")` finds all sections with `#exchange` anywhere in any chain.
- **Direct children** (`.*`) — replaced by trailing `#`. `.filter("#exchange#")` finds sections where `#exchange` is followed by exactly one more segment.
- **Character completion / autocomplete** — this is an app-layer concern. The app calls `view.tags()` to get all unique tags, then does prefix matching in the UI. FlexTag doesn't need to implement autocomplete in its query engine.

### Dot Hierarchy: Removed

The dot-separated hierarchy (`#a.b.c`) is replaced entirely by `#`-chains. There is no longer a distinction between "atomic namespace" (dot) and "searchable group" (chain) — all hierarchical tags use `#` chains and all segments are searchable.

If a user wants a truly atomic, unsearchable-by-segment tag, they just use a flat tag with no chain: `#exchangeNyseAapl`. But there's no practical reason to prevent segment matching.

## New Methods

### `.children()` on FlexView

After filtering, extract the **distinct next-level segment values** from matched tags. This powers cascading dropdowns.

```python
# What makes are available?
view.filter("#make").children()
# → ["ford", "dodge", "chevy"]

# What models does Ford have?
view.filter("#make#ford").children()
# → ["mustang", "f150", "bronco"]

# What years for the Mustang?
view.filter("#make#ford#mustang").children()
# → ["2024", "2025"]
```

`.children()` operates on the **literal stored tag strings** — it looks at matched sections' tags, finds the query segment within each chain, and returns the unique values of the next segment. No hidden data, no expansion. The user can inspect `section.tags` and see exactly where the result came from.

### `.tags()` on FlexView

Return all unique tags across all sections in the view. Powers autocomplete at the app layer.

```python
all_tags = view.tags()
# → ["#make#ford#mustang#2024", "#make#ford#f150#2024", "#make#dodge#charger#2024", ...]

# App-layer autocomplete: filter this list as the user types
```

## Space Sensitivity

Space between tags means **separate, unrelated tags** (existing behavior). No space means **chained, linked segments**:

```flextag
[[#exchange#nyse#aapl #sector#tech]]
```

- `#exchange#nyse#aapl` — one chained tag (three segments)
- `#sector#tech` — another chained tag (two segments)
- `.filter("#aapl")` — matches (segment of first chain)
- `.filter("#tech")` — matches (segment of second chain)
- `.filter("#aapl #tech")` — matches (AND: both segments present)

## Impact on Schema System

### Schema matching with chains

Schema headers use `match_tag()` — they get chain matching automatically. Schemas use the same syntax as filter queries and section headers.

**Base schema — all adapters:**
```flextag
[[#adapter]]: ftml-schema
name: str
[[/]]
```
Matches any section with `#adapter` as a segment in any chain (any depth).

**Direct children schema:**
```flextag
[[#adapter#]]: ftml-schema
adapter_type: str
[[/]]
```
Matches only sections where `#adapter` is followed by exactly one more segment.

**Specific sub-type schema:**
```flextag
[[#adapter#ohlcv]]: ftml-schema
timeframes: [str]
supports_live: bool
[[/]]
```
Matches sections with `#adapter#ohlcv` as a contiguous sub-chain.

**Schema with constrained values (inline OR):**
```flextag
[[#symbol#(nyse|nasdaq|arca|bats|amex|otc)#]]: schema
[[/]]
```
Validates that every symbol section has a recognized exchange and a ticker.

### Layered schema example

```flextag
// Base: all adapters need a name
[[#adapter]]: ftml-schema
name: str
[[/]]

// Specific: ohlcv adapters also need timeframes
[[#adapter#ohlcv]]: ftml-schema
timeframes: [str]
supports_live: bool
[[/]]

// Data section — matches BOTH schemas
[[#adapter#ohlcv#yahoo name="Yahoo Finance" timeframes=["1d","1wk"] supports_live=false]]: ftml
description = "Free market data provider"
[[/]]
```

### Strict mode

Strict mode (`strict=True`) works exactly as it does today — every non-schema section must match at least one schema. The only change is that schemas use chain syntax instead of dot/wildcard syntax.

## Impact on Filter Queries

Filter queries work exactly as they do today for the operators:

- **AND** (space): `.filter("#exchange #sector")` — both must be present
- **OR** (`|`): `.filter("#nyse | #nasdaq")` — at least one
- **Negation** (`!`): `.filter("#adapter !#deprecated")` — has adapter, not deprecated
- **Grouping** (`()`): `.filter("#adapter (#ohlcv | #news)")` — adapter AND one of ohlcv/news

The only change is how tag matching works — segment-based instead of exact/wildcard.

## Backward Compatibility

This is a **breaking change**. Migration:

| Old | New |
|---|---|
| `#exchange.nyse.aapl` | `#exchange#nyse#aapl` |
| `#exchange.*` | `#exchange#` (trailing `#`) |
| `#exchange.**` | `#exchange` (segment match) |
| `#fo*` | app-layer prefix match on `view.tags()` |
| Schema `[[#adapter.**]]` | `[[#adapter]]` |
| Schema `[[#adapter.*]]` | `[[#adapter#]]` |
| Schema `[[#symbol.* (#nyse \| #nasdaq)]]` | `[[#symbol#(nyse\|nasdaq)#]]` |

## Open Questions

1. **Contiguous sub-chain matching** — should `.filter("#exchange#aapl")` match `#exchange#nyse#aapl` (non-contiguous segments)? Or must the segments be adjacent in the chain? Recommendation: require adjacency — `#exchange#aapl` means "exchange directly followed by aapl."
2. **Ordering** — should `.filter("#aapl#exchange")` match `#exchange#nyse#aapl` (reversed order)? Recommendation: no — order matters in chains. If you write `#aapl#exchange`, you're looking for aapl followed by exchange.
3. **How `.children()` handles multiple chains on one section** — if a section has `#exchange#nyse#aapl #sector#tech`, and you filter by `#exchange`, does `.children()` only look at the `#exchange` chain? Recommendation: yes — `.children()` scopes to the chain that matched the query.
4. **Dots in tag names** — with dot hierarchy removed, should dots be allowed as literal characters in tag names? e.g., `#version#2.0`. Recommendation: yes — dots become regular characters since they no longer have syntactic meaning.
