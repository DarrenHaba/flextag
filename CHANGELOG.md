## [0.5.0a1] - 2026-08-24

FlexTag re-based on markdown. A deliberate, breaking simplification: the
format no longer has syntax of its own.

### The format
- A FlexTag file IS a markdown file (`.md`). Front matter (YAML) carries the
  file's metadata and tags, and declares the format: `flextag: 0.5`.
- A section is a fenced code block whose info string is a YAML flow mapping:
  ```` ```yaml {tags: [database], id: prod-db} ````. The fence language types
  the body. Fences without a mapping are prose illustrations.
- Hierarchy is `/` inside a tag (`env/production`); filters match any segment.
- Bad YAML fails loudly with file and line.

### The API
- `flextag.load(path)` — one file or a whole tree -> a `View`.
- `View.filter(tag=..., **meta)`, `.files(...)`, `.values(key)`, `.tags()`,
  `.children(prefix)`; `Section` is plain data (tags, meta, lang, body, file,
  line). The 0.4 query-string language is gone.

### Removed
- The `[[#tag ...]]: type` container, the schema system, FTML integration,
  tag paths (`#a#b`), query strings. The 0.4 reader remains importable as
  `flextag.legacy` (DeprecationWarning on use) and is REMOVED at 0.6 — pin
  `flextag==0.4.0` if you need the old format long-term.

## [0.4.0] - 2026-04-17

Complete rewrite of FlexTag. Nothing is backward compatible with 0.3.x.

### Syntax

- Section headers: `[[#tag param=value]]: type` (IDs removed, tags are identity)
- Closing tags: `[[/]]` (universal, no more `[[/id]]`)
- File metadata: `[[#tags params]]: file-metadata` (replaces `[[]]: container`)
- Comments between sections: `//` prefix (replaces `#` which conflicted with tags)
- Default content type: `text` (replaces `raw`)

### Tags

- `@path` syntax removed — use flat `#tag` names
- `.path` syntax removed — use flat `#tag` names
- Dot hierarchy removed — `#exchange.nyse.aapl` is no longer valid syntax; use flat tags and tagged parameters instead
- Exact match only — `#config` matches `#config`, nothing else
- `!#tag` — negation (exclude sections with tag)
- `(#a | #b)` — OR groups
- `|` pipe operator for top-level OR in filters
- Case-insensitive matching — `#NASDAQ`, `#nasdaq`, `#Nasdaq` all match
- No wildcards — `*`, `.*`, `.**`, `#fo*` are all removed

### Tagged Parameters

- New `tag` parameter type — values prefixed with `#` are tags: `exchange=#nyse`
- Tag search finds parameter values — `.filter("#nyse")` searches standalone tags AND tag-typed parameter values
- Key-value filter — `.filter("exchange=#nyse")` matches specific parameter values
- Key-exists filter — `.filter("exchange=")` matches sections that have the `exchange` parameter (any value)
- `.values(key)` — returns unique values for a parameter key across matched sections (powers cascading dropdowns)
- `.tags()` — returns all unique tags (standalone + parameter tag values) for autocomplete
- String parameters are NOT searchable as tags — only `#`-prefixed values

### Schema System

- Old `[[]]: schema` with field quantifiers (`?`, `+`, `*`) removed entirely
- New `ftml-schema` sections — schemas are regular sections that target by tags
- `[[#product]]: ftml-schema` validates sections with the `#product` tag
- New `schema` content type — metadata-only validation (header params only, body ignored)
- Multiple schemas can match one section (all validated independently)
- Validates both header parameters and FTML body content (`ftml-schema`) or header only (`schema`)
- `|` and `()` for OR groups in schema headers: `[[#product (#electronics | #clothing)]]: ftml-schema`
- `strict=True` load parameter — every section must match at least one schema
- Parameter constraint definitions in schema headers: `[[#item name:str price:float]]: schema`
- `match_tag()` — shared matching logic for filters and schemas

### Content Types

- Built-in types FlexTag parses: `text`, `ftml`, `json`, `yaml`, `toml`, `binary`, `ftml-schema`, `schema`
- Custom types accepted silently — any unrecognized type (e.g. `python`, `css`, `html`) is treated as text, no warning, type string stored as metadata
- Default type is `text` when no type specified
- `:type` filter syntax — `.filter(":python")`, `.filter(":ftml-schema")`, `.filter("#config :yaml")`

### Filtering

- Exact match only — no wildcards, no hierarchy traversal
- `:type` content type filter: `view.filter(":python")`, `view.filter(":ftml-schema")`
- `|` pipe operator for OR: `view.filter("#electronics | #clothing")`
- `()` grouping for OR within AND: `view.filter("#product (#electronics | #clothing)")`
- Case-insensitive string comparisons for `=` and `!=` operators
- Legacy `OR` keyword still supported
- Parameter expressions: `market_cap>1000000`, `type="CS"`

### Other

- `source_path` — exposed on Section and Container (replaces internal `source_name`), full absolute file path string
- `binary` content type (returns `bytes`)
- `recursive` parameter for `load()` with `dir=` (default: True)
- Replaced Black + Flake8 with Ruff
- Multi-Python CI (3.10–3.13), cross-platform (Ubuntu, Windows, macOS)

### Removed

- Section IDs, `@path` syntax, `.path` syntax, single bracket `[]` notation
- `[[]]: defaults` syntax
- Dot hierarchy (`#a.b.c`) — use flat tags + tagged parameters
- Wildcards (`*`, `.*`, `.**`, `#fo*`) — use exact match + tagged parameters
- `to_dict()`, `to_flexmap()`, `FlexMap`, `FlexPoint`
- Encoding types (`utf-8`, `latin-1`, `ascii`, `utf-16`)
- Dependencies: duckdb, numpy, ftml, tomli-w, Black, Flake8

## [0.3.0a1] - 2025-05-20
### BREAKING CHANGES
- Complete restructuring of the FlexTag API and syntax
- No backward compatibility with 0.2.x versions
- Removed all deprecated features and legacy syntax

### Added
- New parameter type system with explicit type annotations (`key:type=value`)
- Support for nullable types with `?` modifier (`key:type?=null`)
- Comprehensive type validation for all parameters
- Standardized path syntax using `@path` prefix exclusively
- Enhanced error messages with more specific details
- Improved FTML content handling and schema validation

### Removed
- Deprecated `.path` syntax (replaced with `@path`)
- Support for boolean flag parameters without explicit values
- Legacy help system and display formatting

### Changed
- All parameter values now require explicit `key=value` format
- Stricter validation for metadata syntax
- Improved performance for large documents
- More consistent error handling throughout the library

## [0.2.2] - 2024-10-17
### Added
- Added links to documentation.
- Updated documentation to fix anchor issues in the README.

## [0.2.1] - 2024-10-17
### Added
- Updated the API reference example to add clarity.
- Updated documentation to fix anchor issues in the README.
- Add CHANGELOG.md to track changes.
- Incremented version number to 0.2.1.

### Fixed
- Anchor links in documentation that led to wrong sections.
