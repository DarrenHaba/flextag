```
flextag/
├── __init__.py
├── exceptions.py
├── logger.py          
├── settings.py          
└── core/
    ├── __init__.py
    ├── compression.py
    ├── factory.py          # FlexTagFactory
    ├── highlighter.py      # FlexTagHighlighter
    ├── base/
    │   ├── compressor.py   # BaseCompressor
    │   ├── container.py    # BaseContainer
    │   ├── parser.py       # BaseFlexTagParser
    │   ├── search.py       # BaseSearchQuery, BaseSearchAlgorithm
    │   ├── section.py      # BaseSection
    │   └── transport.py    # BaseTransportContainer
    ├── impl/
    │   ├── compressor.py   # GzipCompressor, ZipCompressor
    │   ├── container.py    # Container
    │   ├── parser.py       # ContentParser, JSONParser, YAMLParser, FlexTagParser
    │   ├── registry.py     # CompressionRegistry
    │   ├── search.py       # ExactMatchAlgorithm, WildcardMatchAlgorithm
    │   ├── section.py      # Section
    │   └── transport.py    # TransportContainer
    └── interfaces/
        ├── compressor.py   # ICompressor
        ├── container.py    # IContainer 
        ├── parser.py       # IContentParser, IFlexTagParser
        ├── search.py       # ISearchQuery, ISearchAlgorithm
        ├── section.py      # ISection
        └── transport.py    # ITransportContainer    