# FlexTag Format Specification

## Core Concepts

FlexTag is a flexible document format that allows content to be split into sections that can be marked, categorized, and filtered efficiently.

### Elements
- **SETTINGS**: Defines default parameters for the entire document.
- **INFO**: Stores metadata about the document.
- **SEC**: The main content **sections**.

### Markers
- Simple visual syntax for common metadata
- Automatically maps to parameters internally
- Two prefix types: tags (#) and paths (.)

Examples:
```
[[SEC #tag #draft_tag]]        -> {tags=["tag, "draft_tag"]}
[[SEC .docs.guides .path.2]]   -> {path=["docs.guides", "path.2"]}
[[SEC #draft .docs.guides]]    -> {tags=["draft"], path=["docs.guides"]}
```

### Parameters
- Key-value pairs for rich metadata
- Can be used alongside markers
- Special handling for tags/paths

Examples:
```
[[SEC {priority=5}]]
[[SEC #draft {priority=5}]]
[[SEC #draft .docs {priority=5, due="2024-03-01"}]]
```

### Internal Parameters
- **fmt**: Content format (text, yaml, json, toml, etc.)
- **enc**: Encoding (utf-8, latin1, etc.)
- **lang**: Language code (en, en-gb, fr, etc.)
- **Defaults if Absent**:
  - `fmt="text"`
  - `enc="utf-8"`
  - `lang="en"`

### Custom Parameters
- Any key-value pair defined by the user, e.g., `my_key="my value"`

### Element Example
```
[[element markers {parameters} ]]
```

## Document Types

### Editable Document
- **Description**: A multi-line, human-readable version of the FlexTag structure.
- **Usage**: Create and edit content sections, markers, and parameters.

### Transport Document
- **Description**: A processed version (e.g., Base64 encoded, compressed, encrypted) suitable for transport.
- **Usage**: Securely send or store the FlexTag data.
- **Creation**: Use the provided package to convert the editable document into a transport document seamlessly.

## Syntax Overview

### Elements

#### SETTINGS Element

```
[[SETTINGS {parameters} ]]
```

- **Purpose**: Sets default parameters for the entire document.
- **Placement**: Must be the first element if used.

#### INFO Element

```
[[INFO markers {parameters} ]]
content...
[[/INFO]]
```

- **Purpose**: Stores metadata about the document.
- **Markers**: Used for categorization and hierarchical organization of documents.
- **Content**: The actual content, format determined by `fmt` parameter.

#### SEC Element

```
[[SEC markers {parameters} ]]
content...
[[/SEC]]
```

- **Purpose**: Main content sections.
- **Markers**: Used for categorization and hierarchical organization of sections.
- **Content**: The actual content, format determined by `fmt` parameter.

### Markers
- Simple visual syntax for common metadata
- Automatically maps to parameters internally
- Two types: tags (#) and paths (.)

Examples:
```
[[SEC #draft]]                    -> {tags=["draft"]}
[[SEC .docs.guides]]              -> {path=["docs.guides"]}
[[SEC #draft .docs.guides]]       -> {tags=["draft"], path=["docs.guides"]}
```

### Tags (`#tag`)

- **Definition**: Simple labels that categorize content.
- **Characteristics**:
  - Start with `#`.
  - Allowed characters `a-z`, `0-9` and `_`
  - Multiple tags separated by spaces (e.g., `#movies` `#trivia`).
  - Non-hierarchical and flat.
- **Examples**:
  - `#completed`
  - `#needs_review`
  - `#popular`

### Paths (`.path.to.category`)

- **Definition**: Hierarchical markers for organizing content.
- **Characteristics**:
  - Start with `.`.
  - Allowed characters `a-z`, `0-9` and `_`
  - Use dot notation for hierarchy levels.
  - Multiple tags separated by spaces (e.g., `.sci_fi.movies` `.sci_fi.trivia`).
  - Provide structured organization.
- **Examples**:
  - `.user.settings`
  - `.project.documentation`
  - `.env.production`

### Parameters

- **Syntax**:
  - Single-line: `{key="value", key2="value2"}`
  - Multi-line:
    ```
    {
      key="value",
      key2="value2"
    }
    ```
- **Rules**:
  - Enclosed in curly braces `{}`.
  - Key-value pairs are comma-separated.
  - Values are in double quotes.

## Rules and Guidelines

### Ordering within Elements

- **Markers**:
  - Can be in any order.
  - Must start with `#` for tags and `.` for paths.
- **Parameters**:
  - Must come last within the opening tag.

**Valid Examples**:

```
[[SEC #tag1 .path {parameters} ]]
[[SEC .path #tag1 {parameters} ]]
[[SEC #tag1 #tag2 .path.subpath {parameters} ]]
```

**Invalid Examples**:

```
[[SEC {parameters} #tag1 ]]
[[SEC #tag1 {parameters} .path ]]
```

### Line Breaks and Indentation

- **Flexible Line Breaks**: Line breaks are allowed within the opening tag for readability.
- **Indentation**: Use 2 spaces for consistency.
- **No Blank Lines**: Do not include blank lines within the opening tag.
- **Use Breaks Sparingly**: Only break lines with many markers or parameters.

**Example**:

```
[[SEC
  #tag1
  #tag2
  .path.subpath
  {
    key="value",
    key2="value2"
  }
]]
```

### Section Content Rules

- **Content Begins**: Immediately after the opening tag (e.g., `[[SEC]]`).
- **Closing Tag**: Required (e.g., `[[/SEC]]`).
- **Escaping Syntax**: Use a backslash ` \ ` to escape special sequences.

**Example of Escaping**:

```
\[[SEC]] displays as [[SEC]]
```

## Examples

### Simple SEC with Tags

```
[[SEC #python #backend ]]
Python: Batteries Included. 
[[/SEC]]
```

### SEC with Path

```
[[SEC .programming.javascript ]]
JavaScript: The Language of the Web
[[/SEC]]
```

### SEC with Tags and Path

```
[[SEC #crossplatform .programming.java .platforms.jvm .tools.android]]
Java: Write Once, Run Anywhere
[[/SEC]]
```

### Mixed Formats Per Section
```
[[SEC #quiz #title {fmt="text"}]]
"Welcome to the quiz! Please read each question carefully and choose the best answer."
[[/SEC]]

[[SEC #quiz #geography {fmt="toml"}]]
question = "What is the capital of Japan?"
options = ["Tokyo", "Kyoto", "Osaka", "Nagoya"]
answer = "Tokyo"
[[/SEC]]

[[SEC #quiz #science {fmt="yaml"}]]
question: "What planet is known as the Red Planet?"
options:
  - "Earth"
  - "Mars"
  - "Venus"
  - "Jupiter"
answer: "Mars"
[[/SEC]]
```

### Example with SETTINGS, INFO, and SEC

```
[[SETTINGS {fmt="toml", enc="utf-8"} ]]

[[INFO #trivia {creator="quiz-master"} ]]
description = "Trivia game settings"
last_updated = "2024-11-20"
[[/INFO]]

[[SEC #easy #geography #capitals .quiz.general ]]
question = "What is the capital of France?"
options = ["Paris", "Berlin", "Rome", "Madrid"]
answer = "Paris"
[[/SEC]]

[[SEC #hard #science .quiz.general ]]
question = "What is the chemical symbol for gold?"
options = ["Au", "Ag", "Fe", "Hg"]
answer = "Au"
[[/SEC]]
```

## Searching and Referencing

### Storage Model

- **Flat Storage**: Tags and paths are stored as flat lists.
- **Differentiation**: Tags and paths are distinguished by their prefixes (`#` or `.`).

**Example Storage Representation**:

```python
{
  "tags": ["#easy", "#2022"],
  "paths": [".sci_fi.games"],
  "parameters": {...},
  "content": "..."
}
```

### Searching Mechanism

- **Search by Tag**:
  ```python
  document.find("#movie")
  ```
- **Search by Path**:
  ```python
  document.find(".sci_fi.movies")
  ```
- **Combined Search**:
  ```python
  document.find("#2022 .sci_fi")
  ```

### Matching Rules

- **Tags**:
  - Match exact tag names (excluding the `#`).
- **Paths**:
  - Can match partially, exactly, or contain the search term.
  - Use parameters like `match_type="exact"` or `match_type="contains"` for precise matching.

**Example**:

- **Partial Path Match**:
  ```python
  document.find(".sci_fi")
  ```
  - Matches `.sci_fi`, `.sci_fi.movies`, `.sci_fi.games`, etc.

- **Exact Path Match**:
  ```python
  document.find(".sci_fi.movies", match_type="exact")
  ```
  - Matches only `.sci_fi.movies`.

- **Contains Path Match**:
  ```python
  document.find(".movies", match_type="contains")
  ```
  - Matches only `.sci_fi.movies`.




## Best Practices

1. **Use Clear Tags and Paths**:
   - Choose meaningful names for tags and paths.
   - Keep tags concise and paths logically structured.

2. **Combine Tags and Paths for Precision**:
   - Use both when you need to categorize and organize content precisely.

3. **Maintain Consistency**:
   - Stick to a consistent naming convention for both tags and paths.

4. **Leverage SETTINGS for Common Parameters**:
   - Set common parameters in `[[SETTINGS]]` to avoid repetition.

5. **Document Custom Parameters**:
   - If you add custom parameters, consider documenting them in `[[INFO]]` for clarity.

## Escaping Special Characters Syntax in Content


- **Escape `[[SEC` and `[[/SEC`**: Use a backslash ` \ ` before them.
Example
```
[[SEC #flextag #tutorial ]]
Here's an example of how to use the section tag:
\[[SEC #tag ]]
Content here.
\[[/SEC]]
[[/SEC]]
```

## Final Thoughts

By consistently using terminology and adhering to the guidelines, the FlexTag format becomes an accessible and powerful tool for organizing content in documents. Whether you're a beginner or an advanced user, this format offers flexibility and clarity for managing complex data structures.

This format allows users to:
- Organize content with both flat tags and hierarchical paths.
- Define default parameters that apply across the document.
- Override defaults within individual elements as needed.
- Easily search and retrieve content based on tags and paths.

## Advanced Usage

### Overriding Defaults and Inheritance

- **SETTINGS Parameters**: Apply to all `[[INFO]]` and `[[SEC]]` elements unless overridden.
- **Overriding Defaults**: Specify parameters within an element to override the defaults.

**Example**:

```
[[SETTINGS {fmt="json", lang="en"}]]

[[SEC #data .users]]
{
  "name": "John Doe",
  "email": "john@example.com"
}
[[/SEC]]

[[SEC #data .admins {fmt="yaml"}]]
name: "Admin User"
email: "admin@example.com"
[[/SEC]]
```

- The first `[[SEC]]` uses `fmt="json"` from `[[SETTINGS]]`.
- The second `[[SEC]]` overrides the format to `fmt="yaml"`.

## Conclusion

By using the updated terminology and maintaining consistency throughout your documents, FlexTag provides a robust yet user-friendly system for content organization. The combination of tags and paths, along with customizable parameters, allows for precise categorization and easy retrieval of information.

Whether you're organizing simple notes or complex data structures, FlexTag adapts to your needs, making it an ideal choice for a wide range of applications.
