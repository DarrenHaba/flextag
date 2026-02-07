# Syntax Refactor Checklist

## Goals

1. **Remove IDs from sections** - DONE
   - Sections identified by tags/paths/parameters only
   - `[[#tag @path param="value"]]: type` instead of `[[id #tag @path]]: type`

2. **Simplify closing tags** - DONE
   - All sections close with `[[/]]`
   - No ID matching needed

3. **File-level metadata** - DONE
   - `[[]]: file-metadata` for file metadata (renamed from `[[]]: container`)
   - `---meta---` / `---schema---` block syntax removed — use standard sections instead
   - Schema uses `ftml-schema` section type: `[[#tag]]: ftml-schema`

4. **Remove single bracket notation** - DONE
   - Everything uses `[[double brackets]]`

## Files Updated

- [x] `src/flextag/flextag.py` - Parser, Section class, Container class
- [x] `src/flextag/__init__.py` - No changes needed
- [x] `tests/unit/test_flextag.py` - Updated all test syntax
- [x] `tests/unit/test_parser.py` - Updated parser tests
- [x] `tests/unit/test_section.py` - Already using new syntax
- [x] `tests/unit/markup_languages/*.py` - Updated all syntax in tests
- [x] `tests/unit/test_metadata/*.py` - Updated metadata tests
- [x] `README.md` - Updated all examples
- [x] `CHANGELOG.md` - Documented breaking changes

## Known Limitations

- Schema validation (`_validate_traditional_schema`) still matches by section ID internally
  - Since IDs are now empty strings, schema validation needs refactoring to match by tags
  - One schema test is skipped pending this fix

## New Syntax Example

```flextag
[[#plugin #plugins.chart version=1.0 author="someone"]]: file-metadata
[[/]]

[[#notes*]]: ftml-schema
title: str
[[/]]

[[#notes #draft title="My Note"]]
This is a draft note
[[/]]

[[#config]]: yaml
host: localhost
port: 5432
[[/]]
```
