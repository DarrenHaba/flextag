# FlexTag Wildcard Syntax

## Overview

FlexTag uses `#hashtags` with dot-separated hierarchy (e.g., `#vehicle.ford.f150`). This document defines the wildcard syntax for pattern matching against tags — for use in filtering, autocomplete, and hierarchical drill-down UIs.

## Design Principles

- **This is not regex.** The syntax borrows familiar symbols but does not implement or imply a regex engine. There is no character-level quantifier logic, no grouping, no alternation beyond explicit `|` composition.
- **The dot is the hierarchy separator.** It is not a wildcard. `#foo.bar` means "bar" is a child of "foo."
- **Exact match is the default.** If you want `#foo`, write `#foo`. There is no operator for "zero or more" because zero is already handled by writing the tag itself.
- **One symbol, two axes.** The wildcard `*` operates on either characters or hierarchy segments, determined by context (whether it follows a dot or sits within a tag name).

## Syntax

### Exact Match

```
#exchange
```

Matches only the tag `#exchange`. Nothing else.

### Character Wildcard — `*`

When `*` appears within or at the end of a tag name (not immediately after a dot as a standalone segment), it means "any characters from here."

```
#fo*
```

Matches `#foo`, `#four`, `#formula`, `#fox` — any tag whose name starts with `fo`.

This is the autocomplete / tag-completion use case. The user has started typing and wants to see what matches.

There is no single-character wildcard. There's no practical need for "starts with fo and has exactly one more character" in the context of tag metadata. Tags aren't wild text — they're controlled vocabulary that users create or browse. Completion is always "show me what starts with this."

### Hierarchy Wildcard (One Level) — `.*`

When `*` appears as a standalone segment after a dot, it means "exactly one level below."

```
#exchange.*
```

Matches `#exchange.nasdaq`, `#exchange.nyse` — but NOT `#exchange` itself and NOT `#exchange.nasdaq.aapl`.

This is the drill-down use case. You know the parent, and you want to populate a dropdown with its direct children. Once the user selects a child, you query again:

```
#exchange.nasdaq.*
```

Which gives you the next level: `#exchange.nasdaq.aapl`, `#exchange.nasdaq.msft`, etc.

### Hierarchy Wildcard (Any Depth) — `.**`

When `**` appears as a standalone segment after a dot, it means "any number of levels below."

```
#exchange.**
```

Matches `#exchange.nasdaq`, `#exchange.nasdaq.aapl`, `#exchange.nyse.ge`, `#exchange.a.b.c.d` — everything under `#exchange`, at any depth. Does NOT match `#exchange` itself.

This is the bulk filter use case. You want everything in a subtree without drilling down level by level.

## Disambiguation

The dot determines which axis `*` operates on:

| Pattern | Dot before `*`? | Axis | Meaning |
|---------|-----------------|------|---------|
| `#fo*` | No | Characters | Tag name starts with "fo" |
| `#exchange.*` | Yes (standalone) | Hierarchy | One level below exchange |
| `#exchange.**` | Yes (standalone) | Hierarchy | Any depth below exchange |

There is no ambiguity. If `*` is part of a tag name, it's character completion. If `*` is an entire segment after a dot, it's hierarchy traversal.

## Composition with `|` (OR)

For cases where you need to match the parent and its children, compose with `|`:

```
#exchange | #exchange.*
```

Matches `#exchange` itself and its direct children. There is no special operator for "self or children" because exact match already exists and the `|` makes the intent explicit.

## Comparison to Existing Conventions

The syntax is most similar to glob patterns used in file systems and tools like gitignore, Python's `pathlib.glob()`, and bash.

| Glob | FlexTag | Meaning |
|------|---------|---------|
| `fo*` | `#fo*` | Name starts with "fo" |
| `exchange/*` | `#exchange.*` | One level below |
| `exchange/**` | `#exchange.**` | Any depth below |

The hierarchy separator differs (`.` instead of `/`), but the wildcard semantics are the same. Developers familiar with glob, gitignore, or Python's `Path.glob('**/*.js')` will find this syntax immediately recognizable.

## Summary

| Pattern | Matches | Does NOT match |
|---------|---------|----------------|
| `#exchange` | `#exchange` | `#exchanges`, `#exchange.nasdaq` |
| `#ex*` | `#exchange`, `#export`, `#extra` | `#exchange.nasdaq` |
| `#exchange.*` | `#exchange.nasdaq`, `#exchange.nyse` | `#exchange`, `#exchange.nasdaq.aapl` |
| `#exchange.**` | `#exchange.nasdaq`, `#exchange.nasdaq.aapl` | `#exchange` |
| `#exchange.nas*` | `#exchange.nasdaq` | `#exchange.nyse`, `#exchange` |
| `#exchange \| #exchange.*` | `#exchange`, `#exchange.nasdaq` | `#exchange.nasdaq.aapl` |

## Breaking Changes

### `#foo*` meaning changes

**Before:** Self + all descendants (`#foo`, `#foo.bar`, `#foo.bar.baz`)
**After:** Any tag whose name starts with `foo` (`#foo`, `#foobar`, `#food`) — does NOT cross dot boundaries

### `#foo+` removed

**Before:** Immediate children only (`#foo.bar`)
**After:** Use `#foo.*` for one level, `#foo.**` for any depth. The `+` modifier is removed entirely.

### Migration path

| Old syntax | New syntax | Meaning |
|-----------|-----------|---------|
| `#foo*` (hierarchy) | `#foo.**` | All descendants any depth |
| `#foo*` (self + descendants) | `#foo \| #foo.**` | Self and all descendants |
| `#foo+` | `#foo.*` | Direct children only |

This affects:
- Filter queries in application code
- Schema headers (e.g., `[[#product+]]: ftml-schema` becomes `[[#product.*]]: ftml-schema`)
- README examples and documentation

## Implementation

### Changes to `match_tag()` in `flextag.py`

The function currently:
1. Strips `#` prefix
2. Detects `*` or `+` suffix
3. Strips modifier and treats remainder as complete tag name
4. Matches using `==` (exact), `startswith(pat + ".")` (hierarchy)

New logic:
1. Strip `#` prefix
2. Split pattern on `.` into segments
3. **If last segment is `*`** → one level hierarchy: `tag.startswith(parent + ".")` and no additional dots in remainder
4. **If last segment is `**`** → any depth hierarchy: `tag.startswith(parent + ".")`
5. **If `*` is inside a segment (e.g., `fo*`)** → character completion: tag segment starts with prefix before `*`
6. **Combined patterns (e.g., `#exchange.nas*`)** → hierarchy prefix + character completion on last segment

### Changes to schema header parser

Same changes — schema headers use `match_tag()` so they get the new behavior automatically.

### Changes to filter parser

Same — `filter()` delegates to `match_tag()`.

## Testing

### Character completion (`*` in tag name)
- `#fo*` matches `#foo`, `#for`, `#four` — NOT `#f`, NOT `#foo.bar`
- `#f*` matches `#foo`, `#fa`, `#f` — NOT `#foo.bar`
- `#exchange*` matches `#exchange`, `#exchanges` — NOT `#exchange.nyse`

### Hierarchy one level (`.*`)
- `#foo.*` matches `#foo.bar` — NOT `#foo`, NOT `#foo.bar.baz`
- `#exchange.*` matches `#exchange.nasdaq`, `#exchange.nyse` — NOT `#exchange`

### Hierarchy any depth (`.**`)
- `#foo.**` matches `#foo.bar`, `#foo.bar.baz` — NOT `#foo`
- `#exchange.**` matches `#exchange.nasdaq`, `#exchange.nasdaq.aapl` — NOT `#exchange`

### Combined (hierarchy + character completion)
- `#exchange.na*` matches `#exchange.nasdaq`, `#exchange.nano` — NOT `#exchange.nyse`
- `#exchange.nas*` matches `#exchange.nasdaq` — NOT `#exchange.nyse`

### Backward compatibility
- `#foo` exact match — unchanged
- `!#foo` negation — unchanged
- `#foo.bar` exact nested match — unchanged
- `#foo.bar.baz` deep exact match — unchanged
