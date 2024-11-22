```
flextag/
├── __init__.py
├── exceptions.py           # FlexTagError
├── logger.py          
├── settings.py          
├── __init__.py
└── core/
    ├── __init__.py
    ├── compression.py
    ├── interfaces/
    │   ├── __init__.py
    │   ├── section.py      # ISection
    │   ├── document.py     # IContainer
    │   ├── transport.py    # ITransportContainer
    │   └── parser.py       # IParser
    ├── base/
    │   ├── __init__.py
    │   ├── section.py      # BaseSection
    │   ├── document.py     # BaseContainer
    │   ├── transport.py    # BaseTransportContainer
    │   └── parser.py       # BaseParser
    ├── factory.py          # FlexTagFactory
    ├── highlighter.py      # FlexTagHighlighter
    └── impl/
        ├── __init__.py
        ├── section.py      # Concrete Section
        ├── document.py     # Concrete Container
        ├── transport.py    # TransportContainer
        └── parser.py       # Concrete Parser
```