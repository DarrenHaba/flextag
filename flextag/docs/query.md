# FlexTag Query System Implementation

## Overview

The FlexTag query system is built on NumPy for high-performance metadata searching. It uses boolean matrices and vectorized operations to enable fast querying across large datasets.

## Core Components

### Data Structures

- Core Arrays (1D NumPy arrays)
  - `block_ids`: Object array of unique identifiers
  - `file_paths`: Object array of source file paths
  - `content_starts`: Int32 array of content start lines
  - `content_ends`: Object array of content end lines (nullable)

- Boolean Matrices (2D NumPy arrays)
  - `tag_matrix`: Boolean matrix mapping blocks to tags
  - `path_matrix`: Boolean matrix mapping blocks to paths
  - Shape: (num_blocks, num_unique_items)

- Parameter Storage
  - `param_arrays`: Dict of typed NumPy arrays for scalar values
  - `param_objects`: Dict of dicts for non-vectorizable values

## Implementation Details

### Matrix Structure

```
tag_matrix[block_idx, tag_idx] = True/False

         tag_1  tag_2  tag_3
block_0    1      0      1
block_1    0      1      0
block_2    1      1      0
```

### Block Addition

- Process
  1. Append to core arrays
  2. Update unique tags/paths lists
  3. Grow boolean matrices if needed
  4. Set corresponding matrix values
  5. Update parameter storage

- Matrix Growth Strategy
  - Create new matrix with increased dimensions
  - Copy existing data
  - Zero-fill new space
  - Update with new block data

### Query Execution

- Process Flow
  1. Split query on 'AND'
  2. Initialize mask as all True
  3. Process each condition
  4. Combine results with boolean AND

- Condition Types
  - Tags: Use tag_matrix column operations
  - Paths: Use path_matrix column operations
  - Parameters: Use vectorized comparisons

### Wildcard Handling

```python
# Example: #tag_*
pattern = tag.replace('*', '.*')
matches = [i for i, t in enumerate(unique_tags)
           if re.match(f"^{pattern}$", t)]
mask = np.any(matrix[:, matches], axis=1)
```

## Performance Considerations

### Memory Usage

- Boolean Matrices
  - Size = num_blocks × num_unique_items × 1 bit
  - Example: 1M blocks, 1K tags = ~122MB

- Parameter Arrays
  - Size depends on data type
  - Integers: 4 bytes per value
  - Floats: 8 bytes per value
  - Strings: Variable size

### Optimization Strategies

- Matrix Operations
  - Use vectorized operations where possible
  - Avoid loop-based processing
  - Leverage NumPy's boolean indexing

- Memory Management
  - Pre-allocate arrays when size is known
  - Batch process updates
  - Use sparse matrices for very large datasets

## Query Syntax Examples

```python
# Single tag
"#config"  
→ tag_matrix[:, tag_idx]

# Multiple tags
"#config AND #system"
→ tag_matrix[:, tag1_idx] & tag_matrix[:, tag2_idx]

# Path with wildcard
".system.*"
→ np.any(path_matrix[:, matching_paths], axis=1)

# Parameter comparison
"index = 5"
→ param_arrays['index'] == 5
```

## Event Integration

### Manager Events

- Block Parsed Event
  ```python
  {
    'event_type': 'block_parsed',
    'data': {
      'block': DataBlock,
      'file': Optional[str]
    }
  }
  ```

- Event Processing
  1. Extract block metadata
  2. Update data structures
  3. Maintain matrix consistency

## Error Handling

### Common Issues

- Matrix Size Mismatch
  - Cause: Inconsistent growth during updates
  - Solution: Verify matrix dimensions before operations

- Index Out of Bounds
  - Cause: Accessing invalid tag/path indices
  - Solution: Boundary checking in matrix operations

- Broadcasting Errors
  - Cause: Incompatible array shapes
  - Solution: Ensure consistent dimensions in boolean operations

## Future Optimizations

- Potential Improvements
  - Sparse matrix implementation for large datasets
  - Parallel query processing
  - Indexed parameter lookups
  - Query result caching
  - Precomputed common queries

## Code Examples

### Matrix Update
```python
def _update_matrix(self, current_matrix, unique_items, new_items, size):
    new_unique = set(new_items) - set(unique_items)
    if new_unique:
        unique_items.extend(sorted(new_unique))
        new_matrix = np.zeros((size + 1, len(unique_items)), dtype=bool)
        if current_matrix is not None:
            new_matrix[:size, :current_matrix.shape[1]] = current_matrix
        return new_matrix
    return current_matrix
```

### Query Processing
```python
def search(self, query: str) -> List[Dict[str, Any]]:
    conditions = query.split(' AND ')
    mask = np.ones(len(self.block_ids), dtype=bool)
    
    for condition in conditions:
        if condition.startswith('#'):
            tag_idx = self.unique_tags.index(condition[1:])
            mask &= self.tag_matrix[:, tag_idx]
    
    return [self._build_result(idx) for idx in np.where(mask)[0]]
```

## Testing Considerations

- Critical Test Cases
  - Matrix growth correctness
  - Query result accuracy
  - Memory efficiency
  - Edge case handling
  - Event processing reliability

- Performance Benchmarks
  - Block addition speed
  - Query response time
  - Memory usage patterns
  - Scaling characteristics