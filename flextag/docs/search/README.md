Boolean Expression Parsing:

- Proper tokenization of query strings
- Support for parentheses grouping
- Building an expression tree


Operator Precedence:

- NOT has highest precedence
- AND has higher precedence than OR
- Parentheses override default precedence


Group Operations:

- Support for parentheses grouping
- Nested boolean expressions


Complex Queries: Now supports queries like
```
query = SearchQuery("(#prod AND #system) OR (#test AND NOT #deprecated)")
query = SearchQuery("(type='config' AND #system) OR (#test AND environment='prod')")
```
