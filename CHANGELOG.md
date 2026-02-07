## [0.4.0a1] - 2026-02-07

### BREAKING CHANGES
- **Hierarchical tags replace `@path`**: `@path` syntax removed — tags now support dot-separated hierarchy (e.g., `#config.database` replaces `@config.database`). The old `@config` would automatically match `@config.database`, `@config.cache`, etc. Hierarchical tags do not — filtering for `#config` will NOT match a section tagged `#config.database`. To get descendant matching, use `#config*` explicitly
- **Schema system completely redesigned**: The old single `[[]]: schema` section with strict rules and quantifiers (`?`, `+`, `*`) is gone. Replaced with tag-based `ftml-schema` sections — each schema is a regular section that matches by tags and validates header properties. Multiple schemas can coexist, each targeting different tags
- **Section IDs removed**: Sections are identified solely by tags and parameters
- **`container` section type renamed to `file-metadata`**: `[[]]: container` is now `[[#tags params]]: file-metadata` — file-level metadata now lives in the section header like everything else
- New universal closing tag `[[/]]` replaces ID-specific closing tags like `[[/section_id]]`
- Removed single bracket `[]` notation entirely
- Renamed `raw` content type to `text` (default type for sections without explicit type)
- Removed encoding types: `utf-8`, `latin-1`, `ascii`, `utf-16` and their aliases
- Removed `to_dict()`, `to_flexmap()`, `FlexMap`, `FlexPoint` — use `view.sections` and `section.content` instead

### Added
- **Tag matching modifiers**: `#tag` (exact), `#tag*` (self + descendants), `#tag+` (immediate children only)
- **Tag negation**: `!#tag` excludes sections with that tag (works in both filters and schemas)
- **New schema system**: `ftml-schema` section type — schemas are regular sections that target other sections by tag matching. A schema `[[#product*]]: ftml-schema` validates all `#product` descendants. Multiple schemas can apply to the same section (AND logic). Schemas validate both header properties and FTML body content
- **`match_tag()` function**: Shared matching logic used by both filter queries and schema validation — one system, not two
- `binary` content type for raw byte data (returns `bytes` instead of `str`)
- `recursive` parameter for `load()` — recursively search subdirectories when using `dir=` (default: True)
- Schema documentation: `doc/schema/README.md` (user-facing) and `doc/dev/schema/` (dev notes)
- Multi-Python version CI testing (3.10, 3.11, 3.12, 3.13)
- Cross-platform CI testing (Ubuntu, Windows, macOS)
- `noxfile.py` for local multi-version testing
- pytest runs on pre-commit hook
- Replaced Black + Flake8 with Ruff for linting

### Changed
- Section syntax: `[[#tag param=value]]: type` instead of `[[id #tag @path]]: type`
- Closing tag: `[[/]]` instead of `[[/id]]`
- Tags and paths unified under `#tag` with dot-separated hierarchy (e.g., `#plugins.chart`)
- File-level metadata uses standard section header syntax — no more body parsing with single bracket notation
- Default section type is now `text` (functionally same as old `raw`)
- Simplified content type system: `text`, `binary`, and markup types (json, yaml, toml, ftml)
- Simplified API: access sections via `view.sections` and content via `section.content`

### Removed
- `@path` syntax — use `#tag` with hierarchical dots and modifiers instead
- Old `[[]]: schema` system with quantifiers (`?`, `+`, `*`) and strict mode — replaced by `ftml-schema` sections
- Section IDs — use tags (`#tag`) to identify and filter sections
- ID-specific closing tags — all sections close with `[[/]]`
- Single bracket notation `[]`
- `[[]]: container` syntax — renamed to `[[]]: file-metadata`
- `[[]]: defaults` syntax
- `to_dict()` — access parsed content directly via `section.content`
- `to_flexmap()` — use `view.sections` and `view.filter()` instead
- `FlexMap` and `FlexPoint` classes — use direct section access
- Unused dependencies: duckdb, numpy, ftml, tomli-w
- Encoding type aliases and re-encoding logic
- Black and Flake8 (replaced with Ruff)

### Fixed
- Made `tomli` conditional (only installed for Python < 3.11)

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
