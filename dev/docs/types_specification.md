# FlexTag DataType System

## Metadata Parameters

Parameters use dynamic type inference by default:

```
[[section param1="hello" param2=123 param3=3.14 param4=true param5=null]]
```

- Double-quoted values become strings (`param1` → `"hello"`)
- Numbers without decimals become integers (`param2` → `123`)
- Numbers with decimals become floats (`param3` → `3.14`)
- Boolean keywords become booleans (`param4` → `true`)
- Null keyword becomes null (`param5?` → `null`)

Parameters can also have explicit types using the colon syntax:

```
[[section param1:string="hello" param2:int=123 param3:float=3.14 param4:bool=true]]
```

## Nullable Types

Types can be made nullable using the `?` modifier. Nullable types can accept either their specified type or null:

```
[[section name:string="John" age:int?=null height:float?=null active:bool?=null]]
```

## Tables

Tables can specify types in two ways:

### 1. Table-Level Type Declaration

When a type is specified for the entire table, all fields must match that type:

```
[[numbers]]: table.int
value1 = 123
value2 = 456
```

A nullable table type allows null values:

```
[[numbers]]: table.int?
value1 = 123
value2 = null
```

### 2. Field-Level Type Declaration

When the table has no specific type, individual fields can declare their own types:

```
[[person]]: table
name:string = "John"
age:int = 30
height:float? = null
active:bool = true
```

Note: Field-level type declarations are only allowed when the table itself doesn't specify a type:

```
# INCORRECT - cannot mix table type with field types
[[data]]: table.int
value1:int = 123    # Error: cannot specify field type when table type is set
value2:int? = null  # Error: cannot specify field type when table type is set

# CORRECT
[[data]]: table.int?
value1 = 123    # Valid integer
value2 = null   # Valid null
```

## Schema Validation

Schema can define table structures and their types:

```
[[ ]]: schema
[person]: table
name:string = "John"     # Required string
age:int? = null         # Optional integer
active:bool = true      # Required boolean
[/person]

[[person]]: table
name = "John"      # Must be string
age = null         # Can be integer or null
active = true      # Must be boolean
[[/person]]
```

### Basic Types

- `string`: Text values
- `int`: Integer numbers
- `float`: Decimal numbers
- `bool`: Boolean values (true/false)

Any of these types can be made nullable by adding `?` after the type name.
