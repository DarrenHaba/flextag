## [0.4.0a1] - 2026-02-03
### BREAKING CHANGES
- Renamed `raw` content type to `text` (default type for sections without explicit type)
- Removed encoding types: `utf-8`, `latin-1`, `ascii`, `utf-16` and their aliases
- Removed `to_dict()` method and function - use `view.sections` and `section.content` instead
- Removed `to_flexmap()` method and function
- Removed `FlexMap` and `FlexPoint` classes

### Added
- `binary` content type for raw byte data (returns `bytes` instead of `str`)
- Multi-Python version CI testing (3.10, 3.11, 3.12, 3.13)
- Cross-platform CI testing (Ubuntu, Windows, macOS)
- `noxfile.py` for local multi-version testing
- pytest runs on pre-commit hook

### Changed
- Default section type is now `text` (functionally same as old `raw`)
- Simplified content type system: just `text`, `binary`, and markup types (json, yaml, toml, ftml)
- Simplified API: access sections via `view.sections` and content via `section.content`

### Removed
- `to_dict()` - access parsed content directly via `section.content`
- `to_flexmap()` - use `view.sections` and `view.filter()` instead
- `FlexMap` and `FlexPoint` classes - use direct section access
- Unused dependencies: duckdb, numpy, ftml, tomli-w
- Encoding type aliases and re-encoding logic

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
