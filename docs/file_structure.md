```
flextag/
├── __init__.py
├── exceptions.py           # FlexTagError
├── logger.py          
├── settings.py          
├── __init__.py
└── core/
    ├── __init__.py
    ├── interfaces/
    │   ├── __init__.py
    │   ├── section.py      # ISection
    │   ├── document.py     # IContainer
    │   └── parser.py       # IParser
    ├── base/
    │   ├── __init__.py
    │   ├── section.py      # BaseSection
    │   ├── document.py     # BaseContainer
    │   └── parser.py       # BaseParser
    ├── factory.py          # FlexTagFactory
    ├── highlighter.py      # FlexTagHighlighter
    └── impl/
        ├── __init__.py
        ├── section.py      # Concrete Section
        ├── document.py     # Concrete Container
        └── parser.py       # Concrete Parser
```