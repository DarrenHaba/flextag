# FlexTag Development Onboarding

## Project Overview

FlexTag is a bracket-based markup language with sections, tags, and rich querying capabilities. It works with FTML (FlexTag Markup Language) for structured data inside sections.

**Repositories:**
- FlexTag: `C:\projects\_open_source\flextag`
- FTML: `C:\projects\_open_source\ftml`

**Key Files to Read First:**
- Philosophy: `C:\projects\_open_source\ftml\dev\PHILOSOPHY.md`
- The Journey: `C:\projects\_open_source\ftml\dev\THE_JOURNEY.md`

## Current Development Focus

We're refactoring FlexTag's syntax and schema system. The changes must be implemented in order:

### 1. Combine Tags and Paths
**File:** `C:\projects\_open_source\flextag\dev\combine_tags_paths.md`

Unifying `#tags` and `@paths` into a single `#tag` system with modifiers:
- `#tag` = exact match
- `#tag+` = immediate children
- `#tag*` = all descendants

This frees up the `@` prefix for the next change.

### 2. Field Bindings
**File:** `C:\projects\_open_source\flextag\dev\field_bindings.md`

Repurposing `@` for field bindings — linking section headers to content fields:
```flextag
[[#category.electronics @name @price]]: ftml
name: str = "MacBook Pro 16"
price: float = 2499.99
[[/]]
```

Enables queries like: `view.filter("#category* @price > 100")`

### 3. Schema Refactor
**File:** `C:\projects\_open_source\flextag\dev\schema_refactor.md`

Simplifying the schema system from a complex document grammar to simple pattern matching + content validation. One FTML schema syntax validates any content type (FTML, YAML, JSON, TOML).

## Core Principle

Everything is based on Python type hint syntax: `name: type = value`

- Section parameters: `name:str="value"` (no spaces, spaces separate params)
- FTML data: `name: str = "value"` (spaces for readability)
- FTML schema: `name: str` (data minus values)
- Queries mirror section headers (copy, strip types and quotes)

## Real-World Usage

The trading project uses FlexTag: `C:\projects\io\techie_trading_frontend\techie-trading-frontend`

Plugin files are in: `plugins/builtin/*.ft` and `plugins/user/*.ft`

## What's Next

Start with the dev docs in order. Each one explains the problem, the solution, and examples. Ask questions if the docs are unclear — they're drafts.
