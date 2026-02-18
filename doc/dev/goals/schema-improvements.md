# Goal: Schema Improvements

## Background

The schema system was redesigned in 0.4.0a1 to use tag-based matching instead of the old quantifier-based system. The new design is cleaner, but real-world usage (building a 13,000-symbol stock market data file) exposed several gaps that prevent the schema from being useful for data validation.

## Problems

### 1. OR requires duplicating entire schema bodies

To express "section must have `#ohlcv` OR `#news`", you must write the same schema body twice:

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

With 6 stock exchanges, you'd need 6 identical schemas. This doesn't scale.

### 2. No strict mode

Sections that don't match any schema pass through silently. This is fine for files with notes and scratch data, but for structured data files (13,000 stock symbols), there's no way to guarantee every section has the required fields. A malformed section sits quietly until someone queries it and gets a runtime error.

### 3. No metadata-only schema

The only schema content type is `ftml-schema`, which validates FTML body content. There's no way to validate just the FlexTag metadata (tags and parameters) without also requiring an FTML body. If a section uses `:json`, `:yaml`, or `:text`, the body goes unvalidated — but more importantly, you can't express tag/parameter requirements independently of body format.

### 4. IF-THEN framing is misleading

The docs describe schema layering as "IF-THEN (Conditional Layering)." It's not conditional logic — it's just multiple schemas matching the same section and all being validated independently. The IF-THEN label confuses people into thinking there's branching. It should be called "schema composition" or "schema layering."

### 5. No parameter constraints in schema headers

FTML supports `str<min_length=3>`, `int<min=0, max=100>`, `str<enum=["a","b","c"]>`. None of this works on FlexTag header parameters. You can type-check `market_cap:int` but you can't constrain it with `market_cap:int<min=0>`.

## Changes

### Change 1: Add `|` (OR) and `()` (grouping) to schema headers

Use FTML's pipe syntax for OR. AND stays implicit (space-separated tags). Parentheses group OR expressions.

```flextag
// Must have #symbol.* AND one of these exchange tags
[[#symbol.* (#nyse | #nasdaq | #arca | #bats | #amex | #otc)]]: ftml-schema
name: str
type: str
[[/]]
```

Rules:
- `|` means OR — at least one of the alternatives must match
- `()` groups OR expressions — everything outside the group is still AND
- AND is implicit — `#a #b` means both required (unchanged)
- `!` negation works inside groups — `(#a | !#b)` is valid
- Nesting groups is NOT supported — `((#a | #b) | #c)` is invalid, use `(#a | #b | #c)`

Parser change: the schema header parser (and filter parser) needs to handle `(` `)` and `|` tokens. Split on `|` inside parens, each alternative is matched independently, section must match at least one.

### Change 2: Add `schema` content type (metadata-only validation)

```flextag
// Only validates that tag matching criteria are met — body is ignored
[[#symbol.* (#nyse | #nasdaq | #arca)]]: schema
[[/]]

// Validates tags/parameters AND FTML body content
[[#symbol.*]]: ftml-schema
name: str
type: str
list_date: str
[[/]]
```

A `schema` section validates FlexTag metadata only:
- Tag matching (same rules as `ftml-schema`)
- Parameter type checking (same as `ftml-schema`)
- Body content is completely ignored regardless of content type

This means you can validate tags/parameters on `:json`, `:yaml`, `:text` sections — anything. The body format doesn't matter.

An empty `schema` body is valid — it means "just check that the tag criteria match." A non-empty `schema` body would be ignored (or could be treated as documentation/comments).

### Change 3: Add `strict` mode (opt-in)

```python
view = flextag.load(path="symbols.ft", validate=True, strict=True)
```

`strict=True` means: every section that is NOT a schema definition (`schema` or `ftml-schema`) and NOT `file-metadata` must match at least one schema. If a section matches zero schemas, raise a `FlexTagValidationError`.

Default: `strict=False` — current behavior, unmatched sections pass through.

This preserves the flexibility argument from `why-no-strict-mode.md` for casual files while enabling data integrity for structured files.

### Change 4: Parameter constraints in schema headers

Borrow FTML's constraint syntax for header parameters:

```flextag
[[#symbol.* market_cap:int<min=0> employees:int<min=0>]]: schema
[[/]]
```

This reuses FTML's existing constraint parser (`<key=value>` syntax) and applies it to FlexTag header parameters. Header constraint definitions are merged with body property definitions.

### Change 5: Rewrite schema docs

- Replace `logic-with-tags.md` — drop IF-THEN framing, document `|` and `()`, show real examples
- Update `why-no-strict-mode.md` — acknowledge strict mode now exists as opt-in, explain when to use it
- Update `what-schema-is.md` — add `schema` content type alongside `ftml-schema`
- Update `what-schema-is-not.md` — remove "Not Strict Mode" section (it is now, optionally)
- Update main `doc/schema/README.md` — add OR syntax, strict mode, `schema` type

## What Stays The Same

- AND is implicit (multiple tags = all required)
- `!#tag` negation works as-is
- Schema composition works as-is (multiple schemas matching same section, all validated)
- FTML body validation with `ftml-schema` works as-is
- Extra fields in body allowed — schemas only enforce declared fields
- `*` and `**` wildcards — see separate goal doc for wildcard changes

## Implementation Order

1. `|` and `()` in schema headers (and filter queries)
2. `schema` content type
3. `strict=True` load parameter
4. Doc rewrites
5. Parameter constraints (future)

## Real-World Use Case

The stock symbol file (`symbols.ft`) with 13,000 sections should be validatable as:

```flextag
// Every symbol child must have an exchange tag
[[#symbol.* (#nyse | #nasdaq | #arca | #bats | #amex | #otc)]]: schema
[[/]]

// Every symbol child must have these body fields
[[#symbol.*]]: ftml-schema
name: str
type: str
sic_description: str
list_date: str
[[/]]
```

Loading with `strict=True` guarantees every section validates against both schemas. A symbol missing its exchange tag or `name` field raises an error immediately on load.
