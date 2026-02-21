# Goal: Tagged Parameters

## Background

This goal supersedes the original [Tag Chains](tag-chains.md) proposal. During design review of chain tags, a deeper problem emerged: nested/hierarchical tags are being used to encode structured key-value data, which is what parameters already do. Chain tags (`#exchange#nyse#aapl`) are an improvement over dot hierarchy (`#exchange.nyse.aapl`) but still force structured data into a flat labeling system.

The real fix is making parameters first-class searchable citizens — and introducing a `tag` type so parameter values can be searched with `#` just like standalone tags.

## Core Design Principle

**What you write in `[[...]]` is what you search with in `.filter()`.** The section header IS the search query. This principle is preserved — and strengthened, because parameters are now directly searchable too.

## Problem

1. `#exchange.nyse.aapl` is an atomic tag — `.filter("#aapl")` returns nothing
2. Users expect flat searches to work and are confused when they don't
3. Nested tags encode key-value relationships (`exchange=nyse`, `symbol=aapl`) without the benefits of actual key-value pairs (typed values, named keys, independent querying)
4. Chain tags (`#exchange#nyse#aapl`) fix searchability but introduce a TOML-like repetition problem — renaming a category means editing every section that uses it
5. Wildcards (`*`, `**`) add cognitive overhead
6. Users end up duplicating data: `[[#exchange.nyse.aapl #aapl]]` or `[[#aapl symbol="aapl"]]`

## Solution: Tagged Parameters

Instead of encoding structure in tag syntax, use parameters with a new `tag` type. Values prefixed with `#` are tags — searchable by `#name` across all parameters.

### Syntax

```flextag
[[exchange=#nyse symbol=#aapl sector=#tech]]
Apple Inc. market data
[[/]]

[[exchange=#nyse symbol=#goog sector=#tech]]
Alphabet market data
[[/]]

[[exchange=#nasdaq symbol=#msft sector=#tech]]
Microsoft market data
[[/]]
```

- `exchange=#nyse` — parameter `exchange` with a tagged value `#nyse`
- The `#` prefix on the value means it's a tag — searchable via `.filter("#nyse")`
- The key gives it structure — queryable via `.filter('exchange=#nyse')`

### Standalone Tags (Flags)

Bare `#tags` remain for boolean flags — things that don't need a key:

```flextag
[[#draft #featured exchange=#nyse symbol=#aapl]]
Apple Inc.
[[/]]
```

`#draft` and `#featured` are flags — present or not. `exchange` and `symbol` are structured data with named keys and typed values.

### Storage

Parameters are stored as key-value pairs on `section.parameters`, exactly as today. The `#` prefix on a value indicates tag type. Standalone `#tags` are stored on `section.tags`, exactly as today.

```python
section.parameters  # {"exchange": "#nyse", "symbol": "#aapl", "sector": "#tech"}
section.tags        # ["#draft", "#featured"]
```

### Matching / Filtering

```python
# Tag search — finds #aapl in ANY tag or parameter value
.filter("#aapl")
# → matches: has #aapl as a standalone tag OR as any parameter value

# Key=value — explicit parameter match
.filter('symbol=#aapl')
# → matches: symbol parameter equals #aapl

# Key exists — parameter is present (any value)
.filter("symbol=")
# → matches: has a symbol parameter

# AND (space-separated)
.filter('exchange=#nyse sector=#tech')
# → matches: both conditions true

# OR (pipe)
.filter('symbol=#aapl | symbol=#msft')
# → matches: either condition true

# Negation
.filter('#featured !#draft')
# → matches: has #featured flag, does not have #draft flag

# Comparison operators (unchanged from today)
.filter("hp>400")
# → matches: hp parameter greater than 400

# Mixed tags and parameters
.filter('#featured exchange=#nyse')
# → matches: has #featured flag AND exchange is #nyse
```

**Key behavior: `#tag` searches everywhere.** When you write `.filter("#aapl")`, it checks:
1. Standalone tags on the section
2. All parameter values that are tags (prefixed with `#`)

This is why `[[symbol=#aapl]]` doesn't require repeating as `[[#aapl symbol=#aapl]]`. The `#aapl` in the parameter value IS the tag.

### The Symmetry Principle in Action

Copy a section header into a filter, get it back:

```python
# Section:
# [[#draft exchange=#nyse symbol=#aapl sector=#tech]]

.filter('#draft exchange=#nyse symbol=#aapl sector=#tech')
# → returns exactly that section (and any other sections matching all conditions)
```

## What This Replaces

| Old | New | Notes |
|---|---|---|
| `#exchange.nyse.aapl` | `exchange=#nyse symbol=#aapl` | Structured data as parameters |
| `#exchange#nyse#aapl` (chain tags v1) | `exchange=#nyse symbol=#aapl` | Same — parameters, not chains |
| `.filter("#exchange.*")` | `.filter("exchange=")` | Key-exists check |
| `.filter("#exchange.**")` | `.filter("exchange=")` | Same — key-exists, no depth concept |
| `.filter("#exchange.nas*")` | app-layer prefix match on `.values()` | See below |
| `#fo*` (character wildcard) | removed — app layer concern | See below |
| `#exchange#nyse` (chain sub-match) | `exchange=#nyse` | Explicit key-value |

### Wildcards: Removed

Wildcards (`*`, `**`) are no longer needed:

- **All descendants / direct children** — no hierarchy to traverse. Filter by key-exists (`exchange=`) or key-value (`exchange=#nyse`)
- **Character wildcard** (`#fo*`) — app-layer concern. Call `view.values("exchange")` and do prefix matching in the UI

### Dot Hierarchy: Removed

No dots, no chains, no paths. Hierarchical relationships are expressed through parameter keys and values.

### Chain Tags: Not Needed

The v1 chain tag proposal (`#exchange#nyse#aapl`) is superseded. Parameters handle structured data better because:
- Each piece of data has a named key (self-documenting)
- Values are independently searchable via `#tag`
- No TOML-like repetition problem — rename a key or value with find-and-replace
- No new hierarchy syntax to learn
- Drill-down order is flexible (any key, any order) instead of fixed by chain position

## New Methods

### `.values(key)` on FlexView

Return all unique values for a given parameter key across matched sections. Powers cascading dropdowns.

```python
# What exchanges exist?
view.values("exchange")
# → ["#nyse", "#nasdaq"]

# What symbols are on NYSE?
view.filter('exchange=#nyse').values("symbol")
# → ["#aapl", "#goog"]

# What sectors on NASDAQ?
view.filter('exchange=#nasdaq').values("sector")
# → ["#tech", "#retail"]
```

This replaces `.children()` from the chain tags proposal. It's more powerful because you choose which key to drill into — the drill-down order isn't baked into tag structure.

### `.tags()` on FlexView

Return all unique tags across all sections in the view — both standalone tags and tag-typed parameter values. Powers autocomplete at the app layer.

```python
all_tags = view.tags()
# → ["#draft", "#featured", "#nyse", "#nasdaq", "#aapl", "#goog", "#msft", "#tech", "#retail"]

# App-layer autocomplete: filter this list as the user types
```

## Real-World Example: Stock Symbols

### Data sections

```flextag
[[exchange=#nyse symbol=#aapl sector=#tech name="Apple Inc."]]
Market data for Apple.
[[/]]

[[exchange=#nyse symbol=#goog sector=#tech name="Alphabet Inc."]]
Market data for Alphabet.
[[/]]

[[exchange=#nasdaq symbol=#amzn sector=#retail name="Amazon"]]
Market data for Amazon.
[[/]]
```

### Cascading dropdown

```python
# Step 1: What exchanges?
view.values("exchange")
# → ["#nyse", "#nasdaq"]

# Step 2: User picks NYSE — what symbols?
view.filter("exchange=#nyse").values("symbol")
# → ["#aapl", "#goog"]

# Step 3: User picks AAPL — what sectors?
view.filter("symbol=#aapl").values("sector")
# → ["#tech"]
```

### Search box — user types "aapl"

```python
view.filter("#aapl")
# → Apple section (found via parameter value, no duplication needed)
```

### OR filtering

```python
view.filter("symbol=#aapl | symbol=#amzn")
# → Apple and Amazon sections
```

## Real-World Example: Cars

### Data sections

```flextag
[[make=#ford model=#mustang year=2024 trim="GT" hp=480]]
The classic muscle car.
[[/]]

[[make=#ford model=#f150 year=2024 trim="Raptor" hp=450]]
Full-size pickup.
[[/]]

[[make=#dodge model=#charger year=2024 trim="Scat Pack" hp=485]]
Sedan with muscle.
[[/]]

[[make=#chevy model=#corvette year=2025 trim="Z06" hp=670]]
Mid-engine sports car.
[[/]]
```

### Queries

```python
# All Ford vehicles
view.filter("make=#ford")

# What models does Ford make?
view.filter("make=#ford").values("model")
# → ["#mustang", "#f150"]

# Search "mustang" — just works
view.filter("#mustang")
# → Ford Mustang section

# High horsepower
view.filter("hp>450")
# → Charger (485), Corvette (670)

# Fords with high horsepower
view.filter("make=#ford hp>400")
# → Mustang (480), F-150 (450)
```

Note: `year=2024` is not tagged (no `#` prefix) because years aren't something you'd search by tag — you'd use comparison operators like `year>=2024`.

## Impact on Schema System

### Schema matching with tagged parameters

Schema headers use the same filter syntax. A schema matches sections based on parameter presence and values.

**Base schema — all sections with an exchange:**
```flextag
[[exchange=]]: schema
exchange: str
symbol: str
[[/]]
```
Matches any section that has an `exchange` parameter (any value).

**Constrained schema — only recognized exchanges:**
```flextag
[[exchange=(#nyse | #nasdaq | #arca)]]: schema
exchange: str
symbol: str
sector: str
[[/]]
```
Matches sections where `exchange` is one of the listed values.

**Tag-based schema — all drafts need a reviewer:**
```flextag
[[#draft]]: schema
reviewer: str
[[/]]
```
Matches any section with the `#draft` flag.

### Layered schema example

```flextag
// Base: all adapters need a name
[[#adapter]]: schema
name: str
[[/]]

// Specific: ohlcv adapters also need timeframes
[[#adapter type=#ohlcv]]: schema
timeframes: [str]
supports_live: bool
[[/]]

// Data section — matches BOTH schemas
[[#adapter type=#ohlcv source=#yahoo name="Yahoo Finance" timeframes=["1d","1wk"] supports_live=false]]: ftml
description = "Free market data provider"
[[/]]
```

### Strict mode

Strict mode (`strict=True`) works exactly as today — every non-schema section must match at least one schema.

## Impact on Filter Queries

Filter operators are unchanged:

- **AND** (space): `.filter('exchange=#nyse sector=#tech')` — both must match
- **OR** (`|`): `.filter('symbol=#aapl | symbol=#msft')` — at least one
- **Negation** (`!`): `.filter('#adapter !#deprecated')` — has tag, not other tag
- **Grouping** (`()`): `.filter('#adapter (#ohlcv | #news)')` — tag AND one of group
- **Comparison**: `.filter('hp>400 year>=2024')` — numeric operators

The change is that `#tag` searches now look at both standalone tags AND parameter values.

## The `tag` Type

`tag` joins the existing parameter types (`str`, `int`, `float`, `bool`, `null`):

- **Syntax**: value prefixed with `#` — `symbol=#aapl`
- **Storage**: stored as a string with the `#` prefix
- **Schema type**: `symbol: tag` in schema definitions
- **Behavior**: searchable via bare `#name` filter queries
- **Non-tag string values**: `name="Apple Inc."` — regular string, NOT searchable via `#`

In schema definitions:
```flextag
[[exchange=]]: schema
exchange: tag
symbol: tag
sector: tag
name: str
hp: int
[[/]]
```

## Backward Compatibility

This is a **breaking change**. Migration:

| Old | New |
|---|---|
| `#exchange.nyse.aapl` | `exchange=#nyse symbol=#aapl` |
| `#exchange#nyse#aapl` (v1 chains) | `exchange=#nyse symbol=#aapl` |
| `.filter("#exchange.*")` | `.filter("exchange=")` |
| `.filter("#exchange.**")` | `.filter("exchange=")` |
| `#fo*` (character wildcard) | app-layer prefix match on `.values()` |
| Schema `[[#adapter.**]]` | `[[#adapter]]` (standalone tag, matches all with flag) |
| Schema `[[#adapter.*]]` | `[[#adapter]]` (same — no hierarchy) |
| Schema `[[#symbol.* (#nyse \| #nasdaq)]]` | `[[exchange=(#nyse \| #nasdaq) symbol=]]` |

## Exposed Property: `source_path`

Rename internal `source_name` to `source_path` on both `Section` and `Container`. Expose it as a public read-only property.

```python
section.source_path  # "/home/user/project/plugins/user/trading/my-plugin.ft"
```

- Returns the **full absolute path** of the file the section was loaded from
- For string-loaded sections, returns `"<string>"`
- This is the only value guaranteed unique across multi-directory loads
- FlexTag does not interpret or truncate the path — it's returned as a plain string
- Users slice it however they need (e.g., `Path(section.source_path).parts[-2:]`)

This replaces the need for built-in IDs. Users who need a unique identifier can combine `source_path` with a parameter like `id="my-plugin"`. FlexTag doesn't enforce uniqueness — the filesystem does.

**No IDs in syntax.** If a user wants an ID, they create a parameter: `id="my-section"`. There is no special ID syntax (`[[my-id]]`, `[[:my-id]]`, etc.) and no uniqueness enforcement by FlexTag.

## Open Questions

1. **Bare value search** — should `.filter("aapl")` (no `#`, no key) search all parameter values and tags? Or must you always use `#aapl` or `symbol=aapl`? Recommendation: require `#` for tag searches, `key=value` for parameter searches. No bare value search — it's ambiguous.
2. **Tag values in `.values()` output** — should `.values("exchange")` return `["#nyse", "#nasdaq"]` (with `#` prefix) or `["nyse", "nasdaq"]` (stripped)? Recommendation: return with `#` prefix — what's stored is what's returned.
3. **Non-tag parameter value search** — should `.filter("Apple")` find `name="Apple Inc."`? Recommendation: no — use `.filter('name="Apple Inc."')` for string parameters. Only `#`-prefixed values are globally searchable.
4. **OR in parameter values** — should `exchange=(#nyse | #nasdaq)` be valid in section headers (not just schemas)? Or only in filter/schema queries? Recommendation: only in filter/schema queries — section headers should have concrete values.
5. **Multiple values per key** — should `tag=[#draft, #featured]` or similar list syntax be supported? Or keep keys unique with single values? Recommendation: keep unique for now. Use separate keys or standalone tags for multiple flags.
