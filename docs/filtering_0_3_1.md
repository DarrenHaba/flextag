# Filtering System Documentation

## Overview
This section explains how to filter content using parameters, tags, and paths in a consistent and unified system. 
All filters are expressed as parameters, making the system simple and extensible. Tags `#tag` and Paths `.path` are just parameters, 
and paths offer hierarchical filtering for advanced organization.

## Filtering Syntax
Filters are defined using parameter-style syntax in braces `{}`. Here’s the general format:

```plaintext
document.find("{parameter=value, parameter>value, parameter~value}")
```

- **`parameter=value`**: Matches exact values.
- **`parameter>value`**: Matches values greater than `value`.
- **`parameter~value`**: Matches values containing or partially matching `value`.
- **`parameter=value1, value2`**: Matches any value in the list.

## Built-in Parameters
- `tags`: Represents flat tags that categorize content. Tags are always strings.
- `paths`: Represents hierarchical namespaces. Paths must be strings.
- Any other metadata parameters (e.g., `year`, `fmt`) can also be filtered.

## Tags Filtering
Tags are treated like any other parameter. Here are examples:

```plaintext
# Exact match
document.find("{tags=data}")

# Multiple tags
document.find("{tags=data, db}")

# Partial match
document.find("{tags~dat}")
```

## Paths Filtering
Paths allow hierarchical filtering. They are interpreted as namespaces.

### Default Behavior
By default, the filter matches the leftmost (first) level of the path. 
For example:
```plaintext
document.find("{paths=sports}")
```
Matches:
- `.sports`
- `.sports.soccer`
- `.sports.soccer.premier_league`

### Multi-Level Matching
To match deeper levels, specify more of the path:
```plaintext
document.find("{paths=sports.soccer}")
```
Matches:
- `.sports.soccer`
- `.sports.soccer.premier_league`

Does **not** match:
- `.sports.tennis`

### Exact Path Match
Use `==` for exact matches:
```plaintext
document.find("{paths==sports.soccer}")
```
Matches only:
- `.sports.soccer`

### Contains Match
Use `~` for substring matches within the path:
```plaintext
document.find("{paths~soccer}")
```
Matches:
- `.sports.soccer`
- `.sports.soccer.premier_league`
- `.games.soccer`

## Logical Combinations
Combine multiple filters using logical operators:
- `&`: AND
- `|`: OR

Example:
```plaintext
document.find("{tags=data} & {paths=sports}")
```
Matches sections with:
- Tag `data` **AND**
- Path starting with `sports`.

Example:
```plaintext
document.find("{tags=data} | {paths=sports}")
```
Matches sections with:
- Tag `data` **OR**
- Path starting with `sports`.

## Advanced Examples
### Match Sections by Tags and Year
```plaintext
document.find("{tags=db, year=2020}")
```

### Match Sections with Partial Tags and Path Hierarchies
```plaintext
document.find("{tags~data} & {paths=sports.soccer}")
```

### Match Sections with Metadata and Specific Path Levels
```plaintext
document.find("{fmt=toml} & {paths==sports.soccer}")
```

### Match Multiple Tags
```plaintext
document.find("{tags=data, db, sports}")
```

## Default Behavior and Extensibility
- All parameters, including tags and paths, are treated equally.
- Paths are inherently hierarchical, with filtering defaulting to the leftmost level unless specified otherwise.
- Tags are flat, and no hierarchy or inheritance is applied.

## Summary
This unified filtering system provides consistency across tags, paths, and parameters. Paths offer advanced 
hierarchical filtering for structured data, while tags remain flat and flexible for categorization.

This simplicity and flexibility ensure powerful yet intuitive filtering for any document structure.
