## [0.4.0a1] - 2026-02-07

Complete rewrite of FlexTag. Nothing is backward compatible with 0.3.x.

### Syntax

- Section headers: `[[#tag param=value]]: type` (IDs removed, tags are identity)
- Closing tags: `[[/]]` (universal, no more `[[/id]]`)
- File metadata: `[[#tags params]]: file-metadata` (replaces `[[]]: container`)
- Comments between sections: `//` prefix (replaces `#` which conflicted with tags)
- Default content type: `text` (replaces `raw`)

### Tags

- `@path` syntax removed — use `#tag` with dot-separated hierarchy (`#config.database`)
- Exact match by default — `#config` does NOT match `#config.database`
- Glob-style wildcards for filtering and schemas:
  - `#tag` — exact match
  - `#tag.*` — direct children (one level)
  - `#tag.**` — all descendants (any depth)
  - `#fo*` — character wildcard (name starts with prefix)
- `!#tag` — negation (exclude sections with tag)
- Case-insensitive matching — `#NASDAQ`, `#nasdaq`, `#Nasdaq` all match

### Schema System

- Old `[[]]: schema` with field quantifiers (`?`, `+`, `*`) removed entirely
- New `ftml-schema` sections — schemas are regular sections that target by tags
- `[[#product.**]]: ftml-schema` validates all descendants of `#product`
- New `schema` content type — metadata-only validation (header params only, body ignored)
- Multiple schemas can match one section (all validated independently)
- Validates both header parameters and FTML body content (`ftml-schema`) or header only (`schema`)
- `|` and `()` for OR groups in schema headers: `[[#product (#electronics | #clothing)]]: ftml-schema`
- `strict=True` load parameter — every section must match at least one schema
- Parameter constraint definitions in schema headers: `[[#item.* name:str price:float]]: schema`
- `match_tag()` — shared matching logic for filters and schemas

### Filtering

- `view.filter()` uses same wildcard syntax as schemas
- `|` pipe operator for OR: `view.filter("#electronics | #clothing")`
- `()` grouping for OR within AND: `view.filter("#product (#electronics | #clothing)")`
- Case-insensitive string comparisons for `=` and `!=` operators
- Legacy `OR` keyword still supported
- Parameter expressions: `market_cap>1000000`, `type="CS"`

### Other

- `binary` content type (returns `bytes`)
- `recursive` parameter for `load()` with `dir=` (default: True)
- Replaced Black + Flake8 with Ruff
- Multi-Python CI (3.10–3.13), cross-platform (Ubuntu, Windows, macOS)

### Removed

- Section IDs, `@path` syntax, single bracket `[]` notation
- `[[]]: defaults` syntax
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
