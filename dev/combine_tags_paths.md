# FlexTag Syntax Change: Unified Tags

## Old Syntax (v0.4.0a1)

Two prefixes: `#tags` and `@paths`
```flextag
[[#database #production @config.storage]]: ftml
```

- `#tag` = exact match when filtering
- `@path` = prefix match (includes children)

**Problem:** No way to get exact match on paths. If you have `@status.todo` and `@status.todo.done`, you can't filter for ONLY the first one.

## New Syntax (v1.0)

One prefix: `#tags` (can be nested)
```flextag
[[#database #production #config.storage]]: ftml
```

**Filtering:**
- `#tag` = exact match (default)
- `#tag+` = one level deep (immediate children)
- `#tag*` = all descendants

## Examples
```flextag
[[#status.todo]]: text
[[#status.todo.done]]: text
[[#status.archived]]: text
```

**Queries:**
```python
view.filter("#status.todo")      # Only first section (exact)
view.filter("#status+")           # todo and archived (children)
view.filter("#status*")           # All three (descendants)
view.filter("#status.todo+")      # Only done (children of todo)
```

## Why

- Simpler: one concept instead of two
- More powerful: can now get exact matches AND children when needed
- Common UI pattern: drill down hierarchies one level at a time

## Migration

Replace `@` with `#`, add `*` when you want children:
```python
# Old
view.filter("@config")

# New
view.filter("#config*")
```