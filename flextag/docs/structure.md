```
flextag/
├── __init__.py
├── managers/
│   ├── __init__.py
│   ├── base.py         # BaseManager
│   ├── data.py         # DataManager
│   ├── query.py        # QueryManager (renamed from search)
│   └── transport.py    # TransportManager
│
├── core/
│   ├── __init__.py
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── provider.py  # ParserProvider
│   │   └── streaming.py # StreamingParser implementation
│   ├── query/
│   │   ├── __init__.py
│   │   ├── provider.py  # QueryProvider
│   │   └── duckdb.py    # DuckDB implementation
│   └── content/
│       ├── __init__.py
│       ├── provider.py  # ContentProvider
│       └── handler.py   # Content loading implementation
│
└── types/
    ├── __init__.py
    ├── block.py        # DataBlock type
    └── metadata.py     # Metadata types
```