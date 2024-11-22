# FlexTag Format Specification

## Core Concepts

FlexTag is a flexible container format that allows content to be split into sections that can be tagged, categorized, and filtered efficiently.

### Elements
- **SETTINGS**: Defines default parameters for the entire document.
- **INFO**: Stores metadata about the document.
- **SEC**: The main content blocks.

### Components
- **Tags (`#tag`)**: Simple labels for categorizing content.
- **Namespaces (`.namespace.path`)**: Hierarchical paths for organizing content.
- **Parameters**: Key-value pairs that provide additional metadata.

## Syntax Overview

### Structure Elements

#### SETTINGS Element

```
[[SETTINGS {parameters}]]
```

- **Purpose**: Sets default parameters for the entire document.
- **Placement**: Must be the first element if used.
- **Defaults if Absent**:
  - `fmt="text"`
  - `enc="utf-8"`
  - `lang="en"`

#### INFO Element

```
[[INFO tags_and_namespaces {parameters}]]
content...
[[/INFO]]
```

- **Purpose**: Stores metadata about the document.
- **Tags and Namespaces**: Can include both `#tags` and `.namespaces`.
- **Content**: Typically contains key-value pairs or descriptive text.

#### SEC Element

```
[[SEC tags_and_namespaces {parameters}]]
content...
[[/SEC]]
```

- **Purpose**: Main content container.
- **Tags and Namespaces**: Used for categorization and hierarchical organization.
- **Content**: The actual content, format determined by `fmt` parameter.

## Components

### Tags (`#tag`)

- **Definition**: Simple labels that categorize content.
- **Characteristics**:
  - Start with `#`.
  - Non-hierarchical and flat.
  - Can have multiple tags per section.
- **Examples**:
  - `#2022`
  - `#easy`
  - `#hard`

### Namespaces (`.namespace.path`)

- **Definition**: Hierarchical paths for organizing content.
- **Characteristics**:
  - Start with `.`.
  - Use dot notation for hierarchy levels.
  - Provide structured organization.
- **Examples**:
  - `.sci_fi.movies`
  - `.config.api.auth`
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

- **Tags and Namespaces**:
  - Can be in any order.
  - Must start with `#` for tags and `.` for namespaces.
- **Parameters**:
  - Must come last within the opening tag.

**Valid Examples**:

```
[[SEC #tag1 .namespace {parameters}]]
[[SEC .namespace #tag1 {parameters}]]
[[SEC #tag1 #tag2 .namespace.subnamespace {parameters}]]
```

**Invalid Examples**:

```
[[SEC {parameters} #tag1]]
[[SEC #tag1 {parameters} .namespace]]
```

### Line Breaks and Indentation

- **Flexible Line Breaks**: Line breaks are allowed within the opening tag for readability.
- **Indentation**: Use 2 or 4 spaces for consistency.
- **No Blank Lines**: Do not include blank lines within the opening tag.

**Example**:

```
[[SEC
  #tag1
  #tag2
  .namespace.subnamespace
  {
    key="value",
    key2="value2"
  }
]]
```

### Content Rules

- **Content Begins**: Immediately after the opening tag.
- **Closing Tag**: Required (e.g., `[[/SEC]]`).
- **Escaping Syntax**: Use a backslash `\` to escape special sequences.

**Example of Escaping**:

```
\[[SEC]] displays as [[SEC]]
```

## Examples

### Example with SETTINGS, INFO, and SEC

```
[[SETTINGS {fmt="toml", enc="utf-8"}]]

[[INFO #config .env.production {owner="team-a"}]]
description = "Production configuration"
last_updated = "2024-03-18"
[[/INFO]]

[[SEC #api .config.auth {fmt="yaml"}]]
content...
[[/SEC]]

[[SEC #easy #2022 .sci_fi.games]]
Game content...
[[/SEC]]

[[SEC #hard .sci_fi.trivia]]
Trivia content...
[[/SEC]]
```

### Simple SEC with Tags

```
[[SEC #easy #2022]]
Content for easy level in 2022.
[[/SEC]]
```

### SEC with Namespace

```
[[SEC .sci_fi.movies]]
Content about sci-fi movies.
[[/SEC]]
```

### SEC with Tags and Namespace

```
[[SEC #2022 .sci_fi.movies]]
Content about sci-fi movies in 2022.
[[/SEC]]
```

## Searching and Referencing

### Storage Model

- **Flat Storage**: Tags and namespaces are stored as flat lists.
- **Differentiation**: Tags and namespaces are distinguished by their prefixes (`#` or `.`).

**Example Storage Representation**:

```python
{
  "tags": ["#easy", "#2022"],
  "namespaces": [".sci_fi.games"],
  "parameters": {...},
  "content": "..."
}
```

### Searching Mechanism

- **Search by Tag**:
  ```python
  container.find(sec_tags=["#easy"])
  ```
- **Search by Namespace**:
  ```python
  container.find(sec_namespaces=[".sci_fi.movies"])
  ```
- **Combined Search**:
  ```python
  container.find(sec_tags=["#2022"], sec_namespaces=[".sci_fi"])
  ```

### Matching Rules

- **Tags**:
  - Match exact tag names (excluding the `#`).
- **Namespaces**:
  - Can match partially or exactly.
  - Use parameters like `match_type="exact"` for precise matching.

**Example**:

- **Partial Namespace Match**:
  ```python
  container.find(sec_namespaces=[".sci_fi"])
  ```
  - Matches `.sci_fi`, `.sci_fi.movies`, `.sci_fi.games`, etc.
- **Exact Namespace Match**:
  ```python
  container.find(sec_namespaces=[".sci_fi.movies"], match_type="exact")
  ```
  - Matches only `.sci_fi.movies`.

## Best Practices

1. **Use Clear Tags and Namespaces**:
   - Choose meaningful names for tags and namespaces.
   - Keep tags concise and namespaces logically structured.

2. **Combine Tags and Namespaces for Precision**:
   - Use both when you need to categorize and organize content precisely.

3. **Maintain Consistency**:
   - Stick to a consistent naming convention for both tags and namespaces.

4. **Leverage SETTINGS for Common Parameters**:
   - Set common parameters in `[[SETTINGS]]` to avoid repetition.

5. **Document Custom Parameters**:
   - If you add custom parameters, consider documenting them for clarity.

## Escaping Special Characters

- **Escape `[[` and `]]`**: Use a backslash `\` before them.
- **Escape `#` and `.` at Start**:
  ```
  \#not_a_tag
  \.not_a_namespace
  ```

## Final Thoughts

By keeping `[[SETTINGS]]` and `[[INFO]]`, and using `[[SEC]]` for content sections, we streamline the format while making it user-friendly for frequent typing. The use of `#` for tags and `.` for namespaces provides clear differentiation, making the FlexTag format both intuitive and powerful.

This format allows users to:
- Organize content with both flat tags and hierarchical namespaces.
- Define default parameters that apply across the document.
- Override defaults within individual elements as needed.
- Easily search and retrieve content based on tags and namespaces.

Feel free to use this specification as a guide for implementing and utilizing the FlexTag format in your projects.
