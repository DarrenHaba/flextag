# FlexTag Technical Specification

FlexTag is a universal data container system that enables organization, discovery, and transportation of mixed-format content. It provides a consistent way to store, search, and manage any type of data through standardized metadata and parameters.

## Core Components

A FlexTag Data Container consists of three distinct components:

1. **Default Section Parameters [[PARAMS]]**
   - Optional, must be first if present
   - Defines default parameter values for all sections
   - No content, parameters only

2. **Container Metadata [[META]]**
   - Must follow PARAMS (or be first if no PARAMS)
   - Describes the container itself
   - No content, parameters only

3. **Container Sections [[SEC]]**
   - One or more sections containing actual content
   - Can override default parameters
   - Can contain any data format specified by parameters

Basic container structure:
```
[[PARAMS fmt="text" enc="utf-8"]]
[[META title="Ecommerce Project"]]

[[SEC:db_settings #config #dev .system.database fmt="toml"]]
port = 5432
host = "localhost"
[[/SEC]]
```

## Parameter Types

Parameters control behavior and provide metadata. Values are typed according to their syntax:

1. **Strings**
   - Quoted text: `name="value"`
   - Example: `title="My Container"`

2. **Numbers**
   - Integer: `count=42`
   - Double: `value=1.0` or `value=1.0d`
   - Float: `value=1.0f`
   - Decimal: `value=1.0m`

3. **Booleans**
   - Simple true/false: `active=true`

4. **Arrays**
   - Square bracket notation: `values=["one", "two"]`

## Parameter Shorthands

FlexTag provides shorthand syntax for common parameter patterns:

1. **Tags**
   ```
   #config #system  → tags=["config", "system"]
   ```
   - Must match pattern: `[a-z0-9_]`

2. **Paths**
   ```
   .env.database .env.config  → paths=["env.database", ".env.config"]
   ```
   - Must match pattern: `[a-z0-9_]`

### **Tags with Wildcards**

FlexTag supports wildcard searches for tags, allowing prefix, suffix, and infix matching. Wildcards are denoted by an asterisk (`*`) and must follow the `#` symbol.

- **Prefix Match**: `#tag*` → Matches any tag that starts with "tag"
- **Suffix Match**: `#*tag` → Matches any tag that ends with "tag"
- **Infix Match**: `#*tag*` → Matches any tag that contains "tag" anywhere

**Examples:**
```
#config        → tags=["config"]
#conf*         → tags starting with "conf" (e.g., "config", "confidential")
#*fig          → tags ending with "fig" (e.g., "config")
#*fig*         → tags containing "fig" anywhere (e.g., "config", "figure")
```

### **Paths with Wildcards**

FlexTag supports wildcard searches for paths, allowing prefix, suffix, and infix matching. Wildcards are denoted by an asterisk (`*`) and must follow the `.` symbol.

- **Prefix Match**: `.path*` → Matches any path that starts with "path" (e.g., `.path.to.data`, `.pathology`)
- **Suffix Match**: `.*path` → Matches any path that ends with "path" (e.g., `.my.path`, `.your.path`)
- **Infix Match**: `.*path*` → Matches any path that contains "path" anywhere (e.g., `.data.path.to.content`, `.pathway`)

**Examples:**
```
.content            → paths=["content"]
.con*               → paths starting with "con" (e.g., "content", "config")
.*ent               → paths ending with "ent" (e.g., "content")
.*ent*              → paths containing "ent" anywhere (e.g., "content", "intent")
```

## Encoding Handling

FlexTag handles encodings at two levels:

1. **Data Container Format**
    - Sections default to UTF-8 for human readability
    - Each section can specify encoding via `enc` parameter
    - No guaranteed data safety at section level
    - Intended for direct editing and viewing

2. **Transport Container Format**
    - Always uses base64 (default) or base32/16 for entire container
    - Guarantees data integrity during transport/storage
    - Preserves all original encodings when decoded back
    - Not intended for direct editing

## Default Parameters

When not specified in [[PARAMS]], these defaults are used:
```
[[PARAMS fmt="text" enc="utf-8" crypt="" comp="" lang="en"]]
```

## Parameter Delimiter

The space between parameters is the delimiter. 
- `#tags`, `.paths` and parameter keys cannot contain spaces. 
- Spaces are allowed in parameter string values, these are not valid delimiters.

## Section Inheritance Rules

FlexTag uses a clear inheritance hierarchy for parameters:

1. **Section-level parameters**
   - Highest precedence
   - Directly specified in [[SEC]] declaration
   ```
   [[SEC:config #system fmt="yaml"]]  // 'fmt="yaml"' overrides all other sources
   ```

2. **Container Default Parameters**
   - Applied when not specified in section
   - Defined in [[PARAMS]] declaration
   ```
   [[PARAMS fmt="text" enc="utf-8"]]  // Applied unless overridden by section
   ```

3. **System Defaults**
   - Lowest precedence
   - Used when not specified in [[PARAMS]] or [[SEC]]
   ```
   fmt="text"     // Default format
   enc="utf-8"    // Default encoding
   crypt=""       // No encryption
   comp=""        // No compression
   lang="en"      // English language
   ```

## Parameter Precedence

Parameters are evaluated in a specific order:

1. **Explicit Parameters**
   ```
   [[SEC:config
     tags=["system", "database"]
     paths=["config.db"]
     fmt="json"
     custom="value"
   ]]
   ```

2. **Shorthand Parameters**
   ```
   [[SEC:config
     #system #database
     .config.db
     fmt="json"
     custom="value"
   ]]
   ```

Both examples produce identical results. Shorthands are processed after explicit parameters
and merged with any existing values.

## Search and Indexing

FlexTag enables efficient content discovery through layered metadata:

**Section-Level Search**
- Search by tags, paths, or parameters
   ```markdown
   [[SEC:config #system .config.database env="production"]]
   Content...
   [[/SEC]]
   ```
  
- Example search targets:
   - All sections with #system tag
   - All sections with .config.database
   - All sections with env == "production"

**Multi-Container Search**

Containers can have optional metadata.
```
[[META
  #config
  title="Porject Configuration"
  version="1.0.4"
  role="admin"
]]
```

- Just like sections, we can search by tags, paths, or parameters
- Filter containers by any combination of metadata
- Search across multiple containers
- Filter by any combination of metadata
- Example search targets:
  - All containers with `#config` tag
  - All containers with `version` == "1.0.4"
  - All containers with `role` == "admin"

**Cross-Container Search**
  - Search across multiple containers via metadata `[[META]]`
  - Filter by any combination of container and sections metadata
  - Filters by tags, paths, or other parameters
  - Example search targets:
    - All containers with `role` == "admin"
    - All containers with `#config` tag
    - All sections with #system tag

**Efficient Container Metadata Search**

When searching through thousands of Containers, we need to quickly and efficiently identify the [[META]] parameters. 

So properly formatted FlexTag file will have the following sections in this order

```
[[PARAMS
[[META
[[SEC
```

- Start search from the top of the file and search down line by line. 
- Limit search to the first 25 lines to optimize performance.
- If `[[META` if fond stop at that line and read in the metadata.
- If `[[SEC` is found, stop with that line and end the search for metadata.

## Transport and Storage

FlexTag containers can exist in multiple forms while maintaining structure:

### Data Container
  - Purpose: A structured format designed for direct storage, organization, and readability.
  - Features:
    - Standardized structure for consistent data handling.
    - Human-readable format for easy editing and debugging.
    - Direct read/write access.
  - Syntax
  ```
  [[PARAMS fmt="text"]]
  [[META title="Config"]]
  [[SEC:data]]
  content...
  [[/SEC]]
  ```
  - PARAMS: Specifies formatting or configuration details.
  - META: Metadata about the data container (used when searching for container).
  - SEC: Encapsulates a section of content, identified by a tag (data).

### Transport Container
  - Purpose: A self-contained format designed for safely transporting data across systems or networks.
  - Features
  - Includes metadata detailing applied transformations (compression, encryption, encoding)
  - Allows customization per user needs (e.g., choice of algorithms).
  - Encapsulates both metadata and data into a single structure for portability.
  
  ```
  FLEXTAG__META_<encoded_metadata>DATA_<encoded_data>__FLEXTAG
  ```
  - META: Encoded metadata section containing transformation details.
  - DATA: Encoded, compressed, and/or encrypted data.
  - Example Metadata
  ```
  {
    "compression": "zlib",
    "encryption": "aes",
    "encoding": "base64",
    "version": "1.0"
    "checksum": "sha256-hash",
    "created": "timestamp"
  }
  ```
  - compression: Specifies the compression algorithm (e.g., zlib).
  - encryption: Indicates the encryption algorithm (e.g., aes).
  - encoding: Defines the encoding format (e.g., base64).
  - version: Tracks the version of the transport container specification.

### Workflow Overview
  - Encoding Pipeline:
    1. Original Data Container
    2. Compress data (if specified).
    3. Encrypt data (if specified).
    4. Encode data into a transport-safe format (always) (base64 by default).
    5. Generate metadata describing the transformations.
    6. Combine metadata and data into a single transport container: FLEXTAG__META_...DATA_...
  - Decoding Pipeline:
    1. Split at META_ and DATA_ marker
    2. Parse the transport container to extract metadata and data.
    3. Decode the data using the specified format (always) (e.g., base64).
    4. Decrypt the data if encryption was applied.
    5. Decompress the data if compression was applied.
    6. Recover the original data container.
  
### Practical Example
  
  Data Container Example:
  ```
  [[PARAMS fmt="text"]]
  [[META title="Example Config"]]
  [[SEC:data]]
  key=value
  another_key=another_value
  [[/SEC]]
  ```
  
  Transport Container Example:
  ```
  FLEXTAG__META_eyJj124iAiYW...DATA_yiAiAVzAmVz...__FLEXTAG
  ```
  
  - The META_ section encodes the JSON metadata:
  ```
  {
    "compression": "zlib",
    "encryption": "aes",
    "encoding": "base64",
    "version": "1.0"
  }
  ```
  - The DATA_ section contains the transformed data after the pipeline (compressed, encrypted, and encoded).
  
### Data Integrity
  - Content verification during save operations
  - Roundtrip testing ensures encoding correctness
  - Byte-level handling for mixed encodings
  - Section boundary preservation during read/write

## Query System

FlexTag's query system enables intuitive searching across both containers and sections using consistent syntax.

### Basic Operations


Example file `container1.flextag`:
```
[[META:config #prod .sys.conf]]

[[SEC:db #database .sys.db]]
host = "localhost"
[[/SEC]]

[[SEC:api #api .sys.api]]
port = 8080
[[/SEC]]
```
Example file `container2.flextag`:
```
[[META:backup #dev .sys.conf]]

[[SEC:db #database .sys.db]]
host = "backup-host"
[[/SEC]]
```

Example code:
```python
import flextag

# Load containers
containers = flextag.loads(["container1.flextag", "container2.flextag"])

# Find first matching section
section = container.find_first(":config")    # Find first section with id="config"
section = container.find_first("#database")  # Find first section with tag

# Search for all matching sections
sections = container.search("#database")     # Find all database sections
sections = container.search(".sys.db")       # Find all sections with path

# Filter containers by metadata
filtered = containers.filter("#prod")        # Only production containers
```

### Search Syntax

1. **Finding Specific Sections**
   ```python
   # Find first matching section
   container.find_first(":config")                    # By ID
   container.find_first(":config #api .sys.api")      # By ID with additional filters
   
   # Find all matching sections
   container.search("#api")                           # By tag
   container.search("#api AND .sys.api")              # Multiple criteria
   container.search("#api AND active=true")           # With parameters
   ```

2. **Container Filtering**
   ```python
   # Filter containers by metadata
   containers.filter("#prod AND .sys.conf")           # Production system configs
   containers.filter("version>'1.0'")                 # Version filtering
   ```

### Query Components

1. **Section Identifiers**
    - `:id` - Specific section ID
    - `#tag` - Section tags
    - `.path.to.section` - Section paths

2. **Logical Operators**
    - `AND`: Both conditions must match
    - `OR`: Either condition can match
    - `NOT`: Exclude matching conditions

3. **Comparison Operators**
    - `=`, `>`, `<`, `>=`, `<=`: Standard comparisons
    - `IN`, `NOT IN`: Array membership

### Important Notes

1. **Section Search Behavior**
    - `find_first()` returns the first matching section and stops searching
    - `search()` returns all matching sections
    - When using `:id` with additional filters, matches must satisfy all criteria

2. **Container Filtering**
    - `filter()` operates on container metadata only
    - Filtered containers maintain all their sections
    - Filtering is additive - each filter further narrows the container set

3. **Path Matching**
    - Paths match partial hierarchies
    - `.sys` matches `.sys.db` and `.sys.api`

4. **Type Safety**
    - Parameter types are inferred from metadata
    - Comparisons must use compatible types
    - Invalid type comparisons raise errors

## Flat Storage Implementation

FlexTag deliberately uses a flat storage pattern rather than nested hierarchical storage. This design choice enables more efficient searching, reduces complexity in data access patterns, and simplifies content caching.

### Architectural Decision: Self-Contained Sections

FlexTag sections are designed to be fully self-contained units, maintaining their own complete set of parameters rather than inheriting them lazily from their parent container. This architectural decision prioritizes reliability and flexibility over memory optimization.

```json
{
  "id": "config",                    // from [[SEC:config]]
  "tags": ["system", "database"],    // from #system #database
  "paths": ["sys.db", "config.db"],  // from .sys.db .config.db

  // Required parameters (always present in each section)
  "fmt": "text",      // Format of content
  "enc": "utf-8",     // Encoding of content
  "crypt": "",        // Encryption method (if any)
  "comp": "",         // Compression method (if any)
  "lang": "en",       // Language identifier

  // Content storage
  "raw_content": "host = \"localhost\"\nport = 5432",
  "content": null,
  "content_parsed": {
    "host": "localhost",
    "port": 5432
  },

  // Custom parameters
  "params": {
    "env": "production",
    "version": "1.0"
  }
}
```

#### Rationale for Self-Contained Design

1. **Independence**
    - Sections can exist and function without maintaining a connection to their parent container
    - Enables reliable serialization of individual sections
    - Supports future container reassignment

2. **Distributed Systems**
    - Sections can be distributed across different systems
    - No need to maintain container reference or network connection
    - Simplifies caching and state management

3. **Reliability**
    - No risk of parameter loss if container connection is broken
    - Consistent behavior regardless of container state
    - Simplified error handling and validation

4. **Scalability**
    - Sections can be moved between containers without parameter reconciliation
    - Supports independent section versioning
    - Enables parallel processing of sections

#### Trade-offs

1. **Memory Impact**
    - Higher memory usage due to parameter duplication
    - Each section carries full parameter set even when identical
    - Impact increases linearly with number of sections

2. **Benefits**
    - Improved reliability and consistency
    - Simplified architecture and maintenance
    - Better support for distributed scenarios
    - Future-proof for advanced features

### Required Parameters

Every section maintains its own copy of these required parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `fmt`     | "text"  | Content format type |
| `enc`     | "utf-8" | Content encoding |
| `crypt`   | ""      | Encryption method |
| `comp`    | ""      | Compression method |
| `lang`    | "en"    | Content language |

### Implementation Example

```python
class Section:
    DEFAULT_PARAMS = {
        "fmt": "text",
        "enc": "utf-8",
        "crypt": "",
        "comp": "",
        "lang": "en"
    }
    
    def __init__(self):
        self.id = ""
        self.tags = []
        self.paths = []
        # Initialize own copy of required parameters
        self.fmt = self.DEFAULT_PARAMS["fmt"]
        self.enc = self.DEFAULT_PARAMS["enc"]
        self.crypt = self.DEFAULT_PARAMS["crypt"]
        self.comp = self.DEFAULT_PARAMS["comp"]
        self.lang = self.DEFAULT_PARAMS["lang"]
        # Additional parameters
        self.params = {}
        # Content storage
        self.raw_content = ""
        self._content_parsed = None

    def clone(self):
        """Create independent copy of section with all parameters"""
        new_section = Section()
        new_section.id = self.id
        new_section.tags = self.tags.copy()
        new_section.paths = self.paths.copy()
        # Copy all parameters
        new_section.fmt = self.fmt
        new_section.enc = self.enc
        new_section.crypt = self.crypt
        new_section.comp = self.comp
        new_section.lang = self.lang
        new_section.params = self.params.copy()
        new_section.raw_content = self.raw_content
        return new_section
```

The `clone()` method demonstrates how sections can be independently copied and moved between containers while maintaining all their parameters and content.
