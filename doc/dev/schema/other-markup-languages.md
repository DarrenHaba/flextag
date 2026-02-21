# Schema Support for Other Markup Languages

## The Door Is Open

The type system leaves room for validating other content types:

```flextag
// FTML schema validates FTML content
[[#indicator]]: ftml-schema
name: str
period: int = 20
[[/]]

// Could JSON Schema validate JSON content?
[[#config]]: json-schema
{
  "type": "object",
  "properties": {
    "name": {"type": "string"}
  }
}
[[/]]

// Could it validate YAML too?
[[#settings]]: yaml-schema
...
[[/]]
```

The syntax pattern `{format}-schema` naturally extends to other formats. JSON Schema could validate both JSON and YAML content (they share the same data model).

## Why We're Not Doing This (Yet)

**Scope creep.**

FlexTag + FTML is a cohesive system we control. Adding JSON Schema means depending on their spec, their quirks, their versioning (draft-04? draft-07? 2020-12?). That's external baggage we'd have to maintain.

**The ecosystem already exists.**

If someone works in JSON/YAML and wants schema validation, they already have mature tools. VS Code validates JSON against schemas. YAML has its own tooling. These ecosystems are well-established.

**No TOML schema standard.**

JSON Schema can validate both JSON and YAML (they share the same data model). But TOML has no widely-adopted schema standard, so we couldn't offer consistent validation across all markup languages anyway.

**Focus.**

FTML schema is the priority. It's designed for FlexTag, it's readable, and we control it. Ship that first, prove the concept works, then consider expanding.

## Decision

Ship FTML schema support first. See if anyone asks for JSON/YAML schema validation. If there's real demand, revisit this. Don't solve a problem that doesn't exist yet.

The syntax is ready. The implementation can wait.
