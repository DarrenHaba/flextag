# FlexTag Development Guide

This guide covers the development workflow for FlexTag, including testing, versioning, and releasing.

## Project Structure

```
flextag/
├── src/flextag/
│   ├── __init__.py      # Public API, version constants
│   └── flextag.py       # Core implementation
├── tests/
│   └── unit/
│       ├── markup_languages/   # Tests for content type parsing
│       └── test_*.py           # Core functionality tests
├── dev/                 # Development docs (excluded from package)
├── pyproject.toml       # Poetry config, dependencies, tool settings
├── noxfile.py           # Multi-version testing
└── .pre-commit-config.yaml
```

## Development Setup

```bash
# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

## Testing

### Run Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=flextag --cov-report=term-missing

# Run specific test file
poetry run pytest tests/unit/test_flextag.py

# Run specific test
poetry run pytest tests/unit/test_flextag.py::TestClassName::test_method
```

### Multi-Version Testing

```bash
# Run tests across Python 3.10, 3.11, 3.12, 3.13
poetry run nox
```

## Linting

We use Ruff for linting (replaces flake8 + black).

```bash
# Check for issues
poetry run ruff check src/ tests/

# Auto-fix issues where possible
poetry run ruff check --fix src/ tests/
```

## Pre-Commit Hooks

Pre-commit runs automatically on `git commit`:
1. **Ruff** - Linting with auto-fix
2. **Pytest** - All tests must pass

To run manually:
```bash
poetry run pre-commit run --all-files
```

## Making Changes

### Before Starting Work

1. Create a feature branch from `main`
2. Run tests to ensure clean starting state

### During Development

- Write tests for new functionality
- Run `poetry run pytest` frequently
- Keep commits focused and atomic

### Before Committing

1. Run linting: `poetry run ruff check --fix src/ tests/`
2. Run tests: `poetry run pytest`
3. Update tests if behavior changed

## Versioning

FlexTag uses semantic versioning with alpha/beta suffixes:
- `0.4.0a1` - Alpha release (breaking changes expected)
- `0.4.0b1` - Beta release (API stabilizing)
- `0.4.0` - Stable release

### Version Locations (update all three)

1. `pyproject.toml` line 3:
   ```toml
   version = "0.4.0a1"
   ```

2. `src/flextag/__init__.py` lines 25-26:
   ```python
   FLEXTAG_VERSION = "0.4.0a1"
   PACKAGE_VERSION = "0.4.0a1"
   ```

### When to Bump Versions

- **Patch** (0.4.0 → 0.4.1): Bug fixes, no API changes
- **Minor** (0.4.0 → 0.5.0): New features, backward compatible
- **Major** (0.x → 1.0): Breaking changes (after 1.0)
- **Alpha increment** (0.4.0a1 → 0.4.0a2): Continued alpha development

## Release Workflow

### Pre-Release Checklist

1. **Update version** in all three locations
2. **Update CHANGELOG.md**
   - Add new version section with date
   - Document breaking changes prominently
   - List added, changed, removed, fixed items
3. **Update README.md** if needed
   - Version badge/warning
   - New feature documentation
   - API changes
4. **Run full test suite**
   ```bash
   poetry run pytest
   poetry run nox  # Multi-version testing
   ```
5. **Run linting**
   ```bash
   poetry run ruff check src/ tests/
   ```

### Publishing

```bash
# Build the package
poetry build

# Publish to PyPI
poetry publish
```

### Post-Release

1. Create git tag: `git tag v0.4.0a1`
2. Push tag: `git push origin v0.4.0a1`

## Changelog Format

```markdown
## [0.4.0a1] - 2026-02-03
### BREAKING CHANGES
- List breaking changes prominently at top

### Added
- New features

### Changed
- Modified behavior

### Removed
- Removed features/APIs

### Fixed
- Bug fixes
```

## Common Tasks

### Adding a New Content Type

1. Add type to `MARKUP_TYPES` or `BASIC_TYPES` in `flextag.py`
2. Add parsing logic in `_parse_content()` method
3. Add tests in `tests/unit/markup_languages/`
4. Document in README.md

### Modifying the Filter Query Language

1. Update `_parse_filter_query()` in `flextag.py`
2. Add tests for new query syntax
3. Update README filtering documentation

### Adding New Section Metadata

1. Update regex patterns in `PATTERNS` dict
2. Update `_parse_header()` method
3. Add to `FlexSection` class if needed
4. Update schema validation if applicable
5. Add tests and documentation
