# FlexTag Parser Implementation

## Overview
A high-performance streaming parser for FlexTag format that achieves ~430,000 blocks/second with minimal memory footprint (~16MB for 1M blocks).

## Core Components

### 1. Metadata String Extraction
- Extracts metadata between `[[DATA` and `]]`
- Handles both single-line and multi-line metadata blocks
- Preserves JSON formatting while cleaning other whitespace

### 2. Block Structure
```
[[DATA:id1, #tag1, .path1, {"key": "value1"}]]
Content lines here...
[[/DATA]]
```

### 3. Parser Implementation
```python
class StreamingFlexTagParser:
    def parse_stream(self, lines_iter):
        current_block = None
        line_number = 0
        
        for line in lines_iter:
            if line.startswith('['):
                if line.startswith('[[DATA'):
                    # Extract and parse metadata
                    # Note content start
                elif line == '[[/DATA]]':
                    # Note content end
                    # Yield block
```

## Key Features

### Performance Characteristics
- Processing Speed: ~430,000 blocks/second
- Memory Usage: ~16MB for 1M blocks
- Comparable to JSON parsing (2.3s vs 1.7s for 1M blocks)

### Design Decisions
1. **Streaming Processing**
   - Line-by-line processing
   - No full file loading
   - Minimal memory footprint

2. **Metadata Parsing**
   - Fast string operations
   - Efficient JSON handling
   - Marker-based parsing (`:`, `#`, `.`)

3. **Output Format**
```python
{
    "id": "example_id",
    "tags": ["tag1", "tag2"],
    "paths": ["path.to.file"],
    "parameters": {"key": "value"},
    "content_start": line_number,
    "content_end": line_number
}
```

## Implementation Notes

### Parsing Strategy
1. **First Pass**: Quick check for `[` character
2. **Second Check**: Verify `[[DATA` start tag
3. **Metadata Extraction**: Process from `[[DATA` to `]]`
4. **Content Tracking**: Track line numbers for content bounds

### Optimization Techniques
1. Minimal string operations
2. Efficient line iteration
3. No regex overhead
4. Direct string method usage
5. Right-to-left search for closing brackets

### Memory Management
1. Stream processing without accumulation
2. No temporary lists or buffers
3. Immediate yield of parsed blocks
4. Garbage collection friendly

## Usage Example
```python
parser = StreamingFlexTagParser()

with open('file.txt') as f:
    for block in parser.parse_stream(f):
        process_block(block)
```

## Performance Comparison
```
Operation          Time (1M blocks)    Memory
FlexTag Parser     2.3 seconds        16MB
JSON Parser        1.7 seconds        Varies
```

## Development Notes
- Attempted Cython optimization but pure Python performed better
- Considered but rejected: regex, multiprocessing, batch processing
- Focused on maintainability and simplicity without sacrificing performance

## Future Considerations
1. Error handling improvements
2. Validation options
3. Custom marker support
4. Content streaming options

## Conclusion
The implementation achieves near-JSON parsing speeds while handling a more complex format, maintaining low memory usage, and keeping code maintainable.