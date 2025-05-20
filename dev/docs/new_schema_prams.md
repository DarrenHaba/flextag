# FlexTag Parameters and Schema System

## Parameter Syntax in Section Headers

Parameters in section headers define key-value pairs with optional type constraints.

### Basic Syntax
```flextag
[[section_name key="value" count=42 active=true]]
```

Parameters use automatic type inference:
- `key="value"` - String (requires double quotes)
- `key=42` - Integer
- `key=3.14` - Float
- `key=true` or `key=false` - Boolean
- `key=null` - Null value

### Parameter Type Inference
```flextag
[[section_id 
  name="admin"          # String (requires double quotes)
  count=42              # Integer
  score=3.14            # Float
  active=true           # Boolean (true or false)
  age=null              # Null value
]]
```

### Typed Parameters
```flextag
[[section_id 
  name:str="admin"      # String type
  count:int=42          # Integer type
  score:float=3.14      # Float type
  active:bool=true      # Boolean type
]]
```

### Nullable Parameters
Add `?` after the type to allow null values:
```flextag
[[section_id
  optional:str?=null    # Can be string or null
  count:int?=42         # Can be integer or null
  score:float=3.14      # Can be float or null
  active:bool=true      # Can be boolean on null
]]
```

## Schema System

The schema system provides comprehensive validation across multiple layers of your FlexTag document:

1. **Section Order Validation**
    - Enforces the required sequence of sections
    - Controls how many times sections can appear (using ?, *, +)

2. **Metadata Validation**
    - Validates required tags, paths, and parameters for each section
    - Ensures parameter types and values match requirements
    - Adds type safety to metadata fields

3. **Content Type Validation**
    - Enforces section content types (raw or yaml)
    - Ensures sections contain appropriate content for their type

4. **YAML Content Validation**
    - Validates the structure of YAML content
    - Enforces field presence and types
    - Validates nested objects and arrays
    - Adds type safety to YAML fields

The schema uses an extended syntax that builds on the parameter system while adding powerful validation capabilities across all these layers.

### Basic Schema Structure
```flextag
[[]]: schema
# Required section
[status=]              # Must have 'status' parameter with any value

# Optional section (note the ? after the bracket)
[priority=]?           # May have 'priority' parameter

# Section with typed parameter
[count:int=]           # Must have 'count' as integer

# Section with specific value
[level="info"]         # Must have 'level' exactly "info"

# Multiple parameters
[status= priority:int=] # Must have both parameters
[[/]]
```

### Repetition Rules
```flextag
[[]]: schema
[params=]     # Exactly one occurrence
[params=]?    # Optional (0 or 1)
[params=]*    # Zero or more
[params=]+    # One or more
[[/]]
```

### YAML Content Validation
```flextag
[[]]: schema
[config]: yaml
  # Required fields
  name:str=         # Required string, any value
  count:int=42     # Required integer, must be 42
  
  # Optional fields (note the ? after field name)
  email?:str=      # Optional string
  age?:int?=      # Optional, nullable integer
  
  # Nested objects
  settings:map={
    theme:str="dark",
    debug:bool=false
  }
  
  # Arrays
  tags:seq.str=[]    # Array of strings
  scores:seq.int=[]  # Array of integers
[[/]]
```

### Schema Features Unique to Parameters
In schema definitions:
- `key=` means "parameter must exist with any value"
- `key:type=` means "parameter must exist with specified type"
- `key=value` means "parameter must exactly match value"

### Complete Schema Example
```flextag
[[]]: schema
# Section requiring specific parameters
[status= priority:int= level="info"]: yaml
  name:str=               # Required string field
  age?:int=              # Optional integer field
  settings:map={
    theme:str="light",
    debug:bool=true
  }
[[/]]+                    # One or more occurrences

# Optional section with nullable parameter
[metadata level:str?=]?

# Multiple required logs
[log timestamp:str= level="debug"]*
[[/]]
```

## Best Practices

1. In regular sections:
    - Use clear, descriptive parameter names
    - Use type annotations when parameter type is important
    - Use nullable types (`type?`) when null is meaningful

2. In schemas:
    - Use `key=` to validate parameter presence
    - Use `key:type=` to validate type
    - Use `key=value` to validate exact values
    - Be explicit about repetition rules

3. Naming conventions:
    - Use lowercase for parameter names
    - Use underscores for multi-word parameters
    - Be consistent with type annotations