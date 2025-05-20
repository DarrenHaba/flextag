# Future Data Types

FlexTag's core types (text, list, dict) provide a foundation for simple data structures.
Future versions will extend this foundation to support more specialized data formats:

Note that the syntax for the future data types is hypothetical, it will need to be refined before implemented.

## DataFrame
Support for pandas/polars style data frames with typed columns

```
[[data]]: dataframe
columns = ["id", "name", "score"]
types = ["int", "string", "float"]
1, "Alice", 95.5
2, "Bob", 87.3
[[/data]]
```

DataFrames will support:
- Column definitions with types
- Missing value handling
- Direct conversion to/from pandas/polars

## Table
SQL-compatible table structures with schema support

```
// SQL-like table
[[users]]: table_sql
schema = {
    "id": "INTEGER PRIMARY KEY",
    "name": "VARCHAR(255)"
}
[1, "Alice"]
[2, "Bob"]
[[/users]]
```

Tables will support:
- Full SQL type system
- Primary/foreign key definitions
- Index specifications
- Direct import/export with SQL databases

## CSV
Native CSV handling with type inference

```
[[data]]: csv
types = ["int", "string", "float"]
id, name, score
1, "Alice", 95.5
2, "Bob", 87.3
[[/data]]
```

CSV support will include:
- Optional headers
- Type inference
- Custom delimiters
- Quoted field handling

## Implementation Notes

These types will be implemented progressively based on user needs.
Each type will maintain FlexTag's core principles:
- Clear, readable syntax
- Strong type safety
- Seamless conversion to/from native formats
- Extensible structure

The goal is to make FlexTag a complete solution for
data serialization while maintaining its simplicity and flexibility.