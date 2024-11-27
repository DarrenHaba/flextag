# FlexTag Project Structure and Design Patterns

## File Structure with Classes

```
flextag/
├── __init__.py              # Version, exports
├── exceptions.py            # FlexTagError, ContainerError, ParameterError, SearchError
├── logger.py               # FlexTagLogger
├── settings.py             # Const (constants)
└── core/
    ├── __init__.py
    ├── types/
    │   ├── __init__.py
    │   ├── metadata.py       # MetadataParameters, Metadata
    │   ├── parameter.py      # ParameterType, ParameterValue
    │   ├── container.py      # Container
    │   └── section.py        # Section
    ├── interfaces/
    │   ├── __init__.py
    │   ├── parser.py         # IContentParser, IMetadataParser, ISectionParser, IContainerParser
    │   ├── search.py         # ISearchQuery, ISearchAlgorithm, ISearchEngine
    │   ├── transport.py      # ITransportContainer, IEncoder, ICompressor
    │   └── managers.py       # IParserManager, ISearchManager, ITransportManager, IRegistryManager
    ├── managers/
    │   ├── __init__.py
    │   ├── parser.py         # ParserManager
    │   ├── search.py         # SearchManager
    │   ├── transport.py      # TransportManager
    │   └── registry.py       # RegistryManager
    ├── parsers/
    │   ├── __init__.py
    │   ├── metadata.py       # MetadataParser
    │   ├── parsers.py        # ContainerParser, SectionParser
    │   └── content/
    │       ├── __init__.py
    │       ├── json.py       # JSONParser
    │       ├── yaml.py       # YAMLParser
    │       └── text.py       # TextParser
    ├── search/
    │   ├── __init__.py
    │   ├── query.py         # SearchQuery
    │   └── algorithms/
    │       ├── __init__.py
    │       ├── exact.py      # ExactMatchAlgorithm
    │       └── wildcard.py   # WildcardMatchAlgorithm
    ├── transport/
    │   ├── __init__.py
    │   ├── container.py      # TransportContainer
    │   └── compression/
    │       ├── __init__.py
    │       ├── gzip.py       # GzipCompressor
    │       └── zip.py        # ZipCompressor
    └── demo/
        ├── __init__.py
        └── ui.py             # FlexTagDemo

## Design Patterns Used

### 1. Manager Pattern
- Used for coordinating complex subsystems
- Each manager is a single source of truth for its domain
- Examples: ParserManager, SearchManager, TransportManager

### 2. Strategy Pattern
- Used for swappable algorithms
- Examples:
  - Search algorithms (Exact vs. Wildcard)
  - Content parsers (JSON, YAML, Text)
  - Compression algorithms (GZip, Zip)

### 3. Registry Pattern
- Used for managing implementations
- Allows runtime registration of components
- Examples: CompressionRegistry, content parser registration

### 4. Factory Pattern
- Used for object creation
- Examples: Container.create(), Section.create()

### 5. Interface Segregation
- Clean separation of interfaces
- Each component has specific responsibilities
- Examples: IContentParser, ISearchAlgorithm

### 6. Dependency Injection
- Components receive their dependencies
- Allows for easy testing and flexibility
- Examples: ParserManager receiving parsers

## Key Architecture Features

### 1. Modularity
- Each component is isolated
- Easy to swap implementations
- Clear separation of concerns

### 2. Extensibility
- Easy to add new:
  - Search algorithms
  - Content parsers
  - Compression methods
  - Transport encodings

### 3. Error Handling
- Centralized error types
- Consistent error propagation
- Detailed logging

### 4. Type Safety
- Strong typing throughout
- Clear interfaces
- Runtime type checking

### 5. Testing Support
- Components designed for testing
- Mockable interfaces
- Isolated components
