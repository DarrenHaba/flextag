# Schema System

The schema system in FlexTag provides powerful validation capabilities for both section structure and content. A schema defines rules for:
- Section presence and repetition
- Required metadata (IDs, tags, paths, params)
- Parameter type safety and validation
- Content type and structure validation

## Basic Schema Structure

Place a schema block near the start of your file (after `container` or `defaults` if present):

```flextag
[[]]: schema
[header #important .docs /]   # Required, exactly once
[meta #info /]?               # Optional (0 or 1)
[entry #data .items /]+       # One or more occurrences
[note #draft /]*              # Zero or more occurrences
[[/]]
```

### Repetition Rules

| Symbol | Meaning                     |
|--------|----------------------------|
| ?      | Optional (0 or 1)         |
| *      | Zero or more              |
| +      | One or more               |
| none   | Exactly one (required)    |

## Content Validation

### Basic Content Types

Specify the content type after the section declaration:

```flextag
[section_id]: raw   # Unstructured text content
[config]: yaml      # Structured YAML content
```

### YAML Content Validation

For sections with `: yaml` type, you can specify detailed field validation:

```flextag
[user]: yaml
name: !!str                    # Required string
email?: !!str                  # Optional string
age: !!int?                    # Required but nullable integer
score: !!float = 0.0          # Required float with default
tags?: !!seq !!str = []       # Optional string array with default
roles: !!seq !!int            # Required integer array
```

#### YAML Type Annotations

- **Basic Types**
    - `!!str` - String
    - `!!int` - Integer
    - `!!float` - Float
    - `!!bool` - Boolean
    - `!!null` - Null value

- **Collection Types**
    - `!!seq !!type` - Array of specified type
    - `!!map` - Object/dictionary

# Todo 

- **Field Modifiers**
    - `?` after field name - Optional field
    - `?` after type - Nullable value
    - `= value` - Default value

## Parameter Type Safety

Parameters in schema sections can now specify type constraints:

```flextag
[section_name
  required_int:int=*           # Any integer
  specific_str:string="admin"  # Must be "admin"
  nullable_float:float?=*      # Any float or null
  version:int=42              # Must be 42
/]
```

### Parameter Type Syntax

```
key:type=value
key:type?=value    # Nullable
```

Where:
- `type`: `int`, `string`, `float`, or `bool`
- `value`: Literal value or `*` for any value of that type
- `?`: Optional indicator for nullable types

## Complete Schema Example

```flextag
[[]]: schema
[user]: yaml
name: !!str                 
age: !!int?                 
scores: !!seq !!float      
metadata: !!map {
  created: !!str,
  updated?: !!str?,
  count: !!int = 0
}
[settings #config
  theme:string="light"     
  debug:bool=*            
  port:int=8080          
/]+
[[/]]
```

This schema:
1. Requires exactly one `user` section with:
    - Required string `name`
    - Nullable integer `age`
    - Array of floats `scores`
    - Object `metadata` with specific field requirements
2. Allows one or more `settings` sections with:
    - String parameter `theme` that must be "light"
    - Boolean parameter `debug` that can be any value
    - Integer parameter `port` that must be 8080