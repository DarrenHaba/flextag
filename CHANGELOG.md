## [0.3.0a1] - 2025-05-20
### ⚠️ BREAKING CHANGES
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
- FlexMap and FlexPoint APIs (marked as deprecated, to be removed in future)

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