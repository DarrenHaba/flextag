```
flextag/
├── __init__.py
└── core/
    ├── __init__.py
    ├── interfaces/
    │   ├── __init__.py
    │   ├── section.py      # ISection
    │   ├── documents.py    # IContainer
    │   └── parser.py       # IParser
    ├── base/
    │   ├── __init__.py
    │   ├── section.py      # BaseSection
    │   ├── documents.py    # BaseContainer
    │   └── parser.py       # BaseParser
    ├── factory.py          # FlexTagFactory
    └── impl/
        ├── __init__.py
        ├── section.py      # Concrete Section
        ├── documents.py    # Concrete Container
        └── parser.py       # Concrete Parser
```