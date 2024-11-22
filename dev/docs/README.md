# FlexTag

FlexTag: The Last Markdown Language You'll Ever Need -- Buckle up because we are creating the 2.0 standards for data management.

## Why FlexTag?
- **No more guessing:** always know exactly what the data is
- **Flat storage:** bypassing nesting for simplicity and scalability.
- **Metadata tagging:** delivering precise context for seamless data management.
- **Encoding compatibility:** supporting everything from UTF-8 to binary with ease.
- **Transport container:** securely bundling any data type into a single, URL-safe line for seamless transfer.


# FlexTag Documentation

## Containers

A FlexTag container is the root element that holds all content. It can be either:
- A string containing FlexTag content
- A file with the `.flextag` extension

Unlike blocks and sections, containers do not use structural tags - the entire string or file itself is the container. There is no explicit start or end marker for containers.

### Container Structure

A container can hold one or more blocks, but blocks cannot be nested. Instead, use metadata tags for hierarchical organization.

Example container with multiple blocks:
```
[[BLOCK #config/db] type=dict fmt=yaml]
database configuration here...

[[BLOCK #config/api] type=dict fmt=json]
api configuration here...
```

### Container Types

FlexTag supports two container types:

1. **Standard Container**
   - Human-readable format
   - Can be a string or .flextag file
   - Preservation of original formatting
   - Suitable for editing and storage
   - Easy to edit with flat structure

2. **Transport Container**
   - Single-line format for transmission
   - Automatic encoding and compression
   - Stores any data type safely
   - System-managed parameters
   - URL safe structured tags and metadata 
   - Embeddable in JSON/YAML
   - Future: encoding support 

### Container Rules

1. Must contain at least one block
2. Blocks are processed sequentially
3. Empty lines between blocks are allowed
4. No container-level metadata or parameters
5. Whitespace preservation within blocks

### Transport Container

The FlexTag Transport Container is a specialized, URL-safe string format designed to encapsulate data for safe and seamless transport. This structure ensures data integrity, preserves the order of operations applied to the data, and remains compatible with embedding in various formats such as JSON, YAML, TOML, Markdown, or transmitting over the web.

#### Structure

Example transport container in Base64

The general structure of a Transport Container is:

```
FLEXTAG_CONT__parameters__content__FLEXTAG_CONT
```

- Start Tag: `FLEXTAG_CONT__`
- Parameters: A series of key-value pairs that describe the operations applied to the data (e.g., compression, encoding).
- Parameter naming: Both key and value names must be in snake_case without any spaces.
- Content: The final processed content after all operations specified in the parameters.
- End Tag: `__FLEXTAG_CONT`

#### Key Components
1. Start and End Tags:
    - The tags `FLEXTAG_CONT__` and `__FLEXTAG_CONT` serve as clear boundaries for the container. They ensure the encapsulated data can be easily identified and extracted.
2. Parameters:
    - The `parameters` section specifies the sequence of operations applied to the content, formatted as `key.value`.
    - Examples:
        - `enc.base64`: Indicates the content has been Base64 encoded.
        - `comp.gzip--enc.base64`: Indicates the content was first compressed using gzip and then encoded using Base64.
    - The order matters:
        - Operations are listed left-to-right in the order they were applied.
        - To reverse the process, operations are applied right-to-left.
3. Content:
    - The actual payload, encoded or compressed based on the parameters.
    - Example:
        - Base64 content: `SGVsbG8sIFdvcmxkIQ==` (encodes `Hello, World!`).
        - Compressed and Base64-encoded content: `eJzT8nEwSM3JyVcozy/KSQEAGgsEXQ==`.

#### Examples

#### Base64 Encoded Only:
```
FLEXTAG_CONT__enc.base64__SGVsbG8sIFdvcmxkIQ==__FLEXTAG_CONT
```

- Input: `Hello, World!`
- Parameter: `enc.base64` (Base64 encoding applied).
- Content: `SGVsbG8sIFdvcmxkIQ==`.

##### Compressed and Encoded:
```
FLEXTAG_CONT__comp.gzip--enc.base64__eJzT8nEwSM3JyVcozy/KSQEAGgsEXQ==__FLEXTAG_CONT
```

- Input: `Hello, World!`
- Parameter: 
    - `comp.gzip`: First compressed using gzip.
    - `enc.base64`: Then encoded using Base64.
- Content: `eJzT8nEwSM3JyVcozy/KSQEAGgsEXQ==`.

#### Order of Operations

The parameter order reflects the sequence of operations applied to the data:

- Left-to-right indicates the operations applied during encoding.
- To decode:
    - Start from the rightmost operation (e.g., decode Base64).
    - Move leftward (e.g., decompress gzip).

##### Example Workflow:

1. To encode: Compress → Encode → Add to container.
2. To decode: Extract from container → Decode → Decompress.

#### URL-Safe and Embedding

- The container format uses only the following characters:
    - Alphanumeric: `a-z`, `A-Z`, `0-9`
    - Symbols: `-`, `_`, `.`
- This ensures compatibility with:
    - Embedding in formats like JSON, YAML, TOML, Markdown, TXT, CSV.
    - Transmission over the web without requiring additional encoding.
- No Spaces: Spaces and other special characters are excluded to avoid parsing errors.
- If additional encoding is necessary (e.g., URL encoding), only apply it to the parameters and ensure it does not alter the Base64-encoded content.

#### Data Safety

- The Transport Container is designed to preserve the integrity of its content:
    - Maintains the original encoding (e.g., UTF-8, Latin-1).
    - Safely encapsulates binary data or text formats without corruption.
- During parsing, the specified format (fmt) determines how the content is interpreted.
- If no format is provided, defaults like UTF-8 are applied.

#### Implementation Notes

- By default, the process for creating a container will
  1. Compress the data (e.g., gzip).
  2. Encode the compressed data in Base64.
  - This ensures the smallest possible size for transport while maintaining compatibility.
- Custom pipelines can omit compression or use alternate encodings if needed.
- Always `validate` the parameters to ensure they match supported operations.


## Blocks and Sections

### Blocks

Blocks are the primary structural elements within a container. Each block starts with the `[[BLOCK]]` structural tag and continues until either another block tag is encountered or the container ends.

#### Basic block structure:
```
[[BLOCK]]
content here...
```

#### Block with tags:
```
[[BLOCK #tag #tag with spaces"]]
content here...
```

#### Block with paths:
```
[[BLOCK #paths/too/content "#paths/too/content/with space"]]
content here...
```

#### Block with parameters:
```
[[BLOCK] type=list fmt=yaml]
- list item 1
- list item 2
```

#### Block split into multiple lines

```
[[BLOCK] type=text fmt=yaml 
enc="numeral system" ver=1.5 lang=us]
```

#### Block split into multiple lines

```
[[BLOCK] 
type=text 
fmt=yaml 
enc="numeral system"
ver=1.5 
lang=us]
```

A block can either:
- Contain regular content in any format (yaml, json, text, flextag, etc.)
- Contain FlexTag sections when format is the default flextag type

### Sections

Sections are subsections that can exist within blocks. They use the `[[SEC]]` structural tag and follow the same metadata and parameter rules as blocks.

Example block with sections:
```
[[BLOCK]]
[[SEC #tag1]]
section content here...
[[/SEC]]

[[SEC #tag2]]
section content here too...
[[/SEC]]
```

Example of multiple blocks with sections:
```
[[BLOCK #tag1]]
[[SEC #tag1]]
block 1, section 1, content here...
[[/SEC]]

[[SEC #tag2]]
block 1, section 2, content here...
[[/SEC]]

[[BLOCK #tag2]]
[[SEC #tag1]]
block 2, section 1, content here...
[[/SEC]]

[[SEC #tag2]]
block 2, section 2, content here...
[[/SEC]]
```

Fun example block with sections storing mixed formats and comments:
```
[[BLOCK]]
[#] Greatest Netflix shows in YAML formated list.
[[SEC #netflix "#greatest shows"] type=list fmt=yaml]
- "Stranger Things"
[#] Yes, Stranger Things is listed above Breaking Bad! 😮
[#] Pause for Internet uproar... okay, back to the YAML list:
- "Breaking Bad"
- "The Crown"
[[\SEC]]

[#] Trivia time! in a JSON fomatted dictionary. 
[[SEC #trivia] type=dict fmt=json]
{"q": "Which Netflix show has the most Emmys?", "a": "The Crown"}
[/*] 
We were both wrong 🤣 The crowd is far more superior 
than both Breaking Bad and Stranger Things 🙌🎉.
[*/]
[[\SEC]]
```

```
[[BLOCK]]
[#] This is a YAML section representing the Enterprise from Star Trek.
[[SEC "#star trek" #sci-fi/ships] type=dict fmt=yaml]
ship: "Enterprise"
captain: "Jean-Luc Picard"
crew:
  - "Data"
  - "Worf"
  - "Geordi La Forge"

engines:
  warp: "9.6"
  impulse: "Full Power"
[[\SEC]]

[#] This is a TOML section representing the Millennium Falcon from Star Wars.
[[SEC "#star wars" #sci-fi/ships] type=dict fmt=toml]
ship = "Millennium Falcon"
captain = "Han Solo"
crew = ["Chewbacca", "Leia Organa"]
engines.hyperdrive = "Class 0.5"
engines.sublight = "Modified Corellian Freighter"
[[\SEC]]

[#] Trivia: Who is the captain of the Millennium Falcon?
[[SEC "#star wars" #sci-fi/trivia] type=dict fmt=json]
{"options": ["Jean-Luc Picard", "Han Solo", "Boba Hutz", "Ewok #42"], "answer": "Han Solo"}
[[\SEC]]
```




#### Block an Section split into multiple lines

```
[[BLOCK] 
type=flextag 
fmt=yaml 
enc="numeral system"
ver=1.5 
lang=us]

[[SEC #long/path/to/something/here] 
type=text fmt=yaml enc="numeral system"
ver=1.5 
lang=us]
- 1
- 2
[[/SEC]]
```

### Metadata and Parameters

Both blocks and sections support metadata tags and parameters:

```
[[BLOCK #config/db "#Production DB"] type=dict fmt=yaml lang=en]

[[SEC #settings "#General Settings"] type=dict fmt=json enc=utf-8]
```

Available parameters for both blocks and sections:
- `type`: Content type (list, dict, text, flextag, etc.)
- `fmt`: Content format (json, yaml, toml, python, etc.)
- `enc`: Encoding (utf8, latin1, etc.)
- `crypt`: Encryption method
- `schema`: Data schema reference
- `ver`: Version identifier
- `lang`: Language code (en, es, fr, etc.)

### Rules and Guidelines

1. Block Rules:
   - Must start with `[[BLOCK]]` structural tag
   - Ends at the next block or container end
   - Cannot be nested within other blocks
   - Must have all parameters on the same line as the tag

2. Section Rules:
   - Must start with `[[SEC]]` structural tag
   - Must end with `[[/SEC]]` structural tag
   - Must be within a block
   - Can only exist in blocks with `fmt=flextag`
   - Cannot be nested within other sections
   - Must have all parameters on the same line as the tag
   - No indentation keep at same level as `[[BLOCK]]`

3. Section Content Rules:
   - All whitespace and tabs are preserved inside: `[[SEC]]` and `[[/SEC]]` tags.
   - Blank lines preserved except final required empty line
   - Content starts on the line after the tag
   - Must escape `[[BLOCK]]`, `[[SEC]]`, `[[SEC]]` with ` \ `
   - Comments tags `[#]`, `[/*]` and `[*/]` ignored by parser, unless escaped  with ` \ `

### Examples

Block with mixed content types:
```
[[BLOCK #documents] fmt=flextag]

[[SEC #code] fmt=python]
# this is python with preserved formatting
def hello_world():
  print("Hello, World!")

[[SEC #config] fmt=yaml type=dict]
server:
  host: localhost
  port: 8080
```

Block with single format:
```
[[BLOCK #api.config] fmt=json type=dict]
{
    "endpoint": "https://api.example.com",
    "timeout": 30,
    "retry": true
}
```

Block with comments:
```
[[BLOCK #api.config] fmt=json type=dict]
[#] flextag comments will be removed when parsed.
{
    "endpoint": "https://api.example.com",
    "timeout": 30,
    [#] This whole line will be removed/ignore by the parser.
    "retry": true
}
[/*] 
Multi-line comments are also 
ignored/removed by the parser.
[*/]
```

Block containing structure tags:
```
[[BLOCK]]

[[SEC #tutorial, #flextag]]
Welcome to this flex tag tutorial.
Let's start off by creating structure tags: 
\[[BLOCK]]

\[[SEC] #tag]
[/*]
Since this content contains structure tags, We must 
escape both of them with the '\' escaped character. 

The same goes for comments too, since we didn't escape 
this opening and closing comment tag this comment will 
be removed by the parser. 
[*/]

/[#] This escaped comment won't be removed by the parser. 

[#] This escaped comment will be removed by the parser.
[[/SEC]]
```

Block containing mixed encodings:
```
[[BLOCK]]

[[SEC #latin1] enc=latin1]]
¡Hola! ¿Cómo estás?
[[/SEC]]

[[SEC #utf8] fmt=utf8]]
你好，世界！
[[/SEC]]

[[SEC #binary] fmt=base64]]
RHVtbnkgYmluYXJ5IGNvbnRlbnQuCg==
[[/SEC]]
```



