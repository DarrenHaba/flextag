import numpy as np
from typing import List, Dict, Any, Optional, Iterator, Set
import re
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class QueryCondition:
    """Represents a parsed query condition"""
    type: str  # 'tag', 'path', 'param', 'group'
    operator: str  # 'AND', 'OR', 'NOT', '=', '>', '<', '>=', '<='
    value: Any
    field: Optional[str] = None  # For parameters

class QueryParser:
    """Parses FlexTag query syntax"""

    def __init__(self):
        self.operators = {'AND', 'OR', 'NOT'}
        self.comparisons = {'=', '>', '<', '>=', '<='}

    def _tokenize(self, query: str) -> List[str]:
        """Convert query string into tokens"""
        # Handle parentheses
        query = query.replace('(', ' ( ').replace(')', ' ) ')
        return [token for token in query.split() if token.strip()]

    def _parse_condition(self, token: str) -> QueryCondition:
        """Parse a single condition token"""
        if token.startswith('#'):
            return QueryCondition('tag', '=', token[1:])
        elif token.startswith('.'):
            return QueryCondition('path', '=', token[1:])
        elif '=' in token or '>' in token or '<' in token:
            # Parameter comparison
            for op in ['>=', '<=', '=', '>', '<']:
                if op in token:
                    field, value = token.split(op)
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            # Keep as string if not numeric
                            pass
                    return QueryCondition('param', op, value, field)
        elif token in self.operators:
            return QueryCondition('operator', token, token)
        elif token in '()':
            return QueryCondition('group', token, token)

        raise ValueError(f"Invalid token: {token}")

    def parse_query(self, query: str) -> List[Dict]:
        """Parse a query string into conditions"""
        parts = query.split(' AND ')
        conditions = []

        for part in parts:
            part = part.strip()
            if part.startswith('#'):
                conditions.append({
                    'type': 'tag',
                    'value': part[1:]
                })
            elif part.startswith('.'):
                conditions.append({
                    'type': 'path',
                    'value': part[1:]
                })
            elif ' = ' in part:
                field, value = part.split(' = ')
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                conditions.append({
                    'type': 'param',
                    'field': field,
                    'operator': '=',
                    'value': value
                })

        return conditions


class BlockStore:
    """Optimized block storage using NumPy"""

    def __init__(self, initial_capacity: int = 10000):
        # Core arrays with pre-allocation
        self.capacity = initial_capacity
        self.size = 0
        self.pending_blocks = []

        # Initialize arrays
        self._init_arrays()

    def _init_arrays(self):
        """Initialize arrays with current capacity"""
        self.block_ids = np.empty(self.capacity, dtype=object)
        self.file_paths = np.empty(self.capacity, dtype=object)
        self.content_starts = np.zeros(self.capacity, dtype=np.int32)
        self.content_ends = np.empty(self.capacity, dtype=object)

        self.unique_tags = []
        self.unique_paths = []
        self.tag_matrix = None
        self.path_matrix = None

        self.param_arrays = {}
        self.param_types = {}

    def _ensure_capacity(self, needed_size: int):
        """Ensure arrays have enough capacity"""
        if needed_size > self.capacity:
            new_capacity = max(needed_size, self.capacity * 2)

            # Resize core arrays
            self.block_ids = np.resize(self.block_ids, new_capacity)
            self.file_paths = np.resize(self.file_paths, new_capacity)
            self.content_starts = np.resize(self.content_starts, new_capacity)
            self.content_ends = np.resize(self.content_ends, new_capacity)

            # Update capacity
            self.capacity = new_capacity

    def _process_batch(self, blocks: List[Dict]):
        """Process a batch of blocks efficiently"""
        if not blocks:
            return

        batch_size = len(blocks)
        new_size = self.size + batch_size
        self._ensure_capacity(new_size)

        # Update core arrays
        for i, block in enumerate(blocks, self.size):
            self.block_ids[i] = block['id']
            self.file_paths[i] = block.get('file_path')
            self.content_starts[i] = block['content_start']
            self.content_ends[i] = block['content_end']

        # Collect all unique tags and paths
        new_tags = set()
        new_paths = set()
        for block in blocks:
            new_tags.update(block['tags'])
            new_paths.update(block['paths'])

        # Update tag matrix
        if new_tags - set(self.unique_tags):
            self.unique_tags.extend(sorted(new_tags - set(self.unique_tags)))
            new_tag_matrix = np.zeros((new_size, len(self.unique_tags)), dtype=bool)
            if self.tag_matrix is not None:
                new_tag_matrix[:self.size, :self.tag_matrix.shape[1]] = self.tag_matrix
            self.tag_matrix = new_tag_matrix
        elif self.tag_matrix is None:
            self.tag_matrix = np.zeros((new_size, len(self.unique_tags)), dtype=bool)
        else:
            self.tag_matrix = np.resize(self.tag_matrix, (new_size, len(self.unique_tags)))

        # Update path matrix similarly
        if new_paths - set(self.unique_paths):
            self.unique_paths.extend(sorted(new_paths - set(self.unique_paths)))
            new_path_matrix = np.zeros((new_size, len(self.unique_paths)), dtype=bool)
            if self.path_matrix is not None:
                new_path_matrix[:self.size, :self.path_matrix.shape[1]] = self.path_matrix
            self.path_matrix = new_path_matrix
        elif self.path_matrix is None:
            self.path_matrix = np.zeros((new_size, len(self.unique_paths)), dtype=bool)
        else:
            self.path_matrix = np.resize(self.path_matrix, (new_size, len(self.unique_paths)))

        # Set values for new blocks
        for i, block in enumerate(blocks, self.size):
            for tag in block['tags']:
                self.tag_matrix[i, self.unique_tags.index(tag)] = True
            for path in block['paths']:
                self.path_matrix[i, self.unique_paths.index(path)] = True

        # Handle parameters
        for block in blocks:
            for key, value in block['parameters'].items():
                if isinstance(value, (int, float, bool)):
                    if key not in self.param_arrays:
                        self.param_arrays[key] = np.empty(self.capacity, dtype=type(value))
                        self.param_types[key] = type(value)
                    self.param_arrays[key][self.size + i] = value

        self.size = new_size

    def add_block(self, block: Dict, file_path: Optional[str] = None):
        """Add a block to storage"""
        block_dict = {
            'id': block.id,
            'tags': block.tags,
            'paths': block.paths,
            'parameters': block.parameters,
            'content_start': block.content_start,
            'content_end': block.content_end,
            'file_path': file_path
        }

        self.pending_blocks.append(block_dict)
        if len(self.pending_blocks) >= self.BATCH_SIZE:
            self._process_batch(self.pending_blocks)
            self.pending_blocks = []

    def flush(self):
        """Process any remaining pending blocks"""
        if self.pending_blocks:
            self._process_batch(self.pending_blocks)
            self.pending_blocks = []

    def search(self, conditions: List[Dict]) -> List[Dict[str, Any]]:
        """Execute a search query"""
        self.flush()  # Ensure all blocks are processed

        # Start with all blocks selected
        mask = np.ones(self.size, dtype=bool)

        for condition in conditions:
            if condition['type'] == 'tag':
                if '*' in condition['value']:
                    pattern = condition['value'].replace('*', '.*')
                    tag_matches = [i for i, t in enumerate(self.unique_tags)
                                   if re.match(f"^{pattern}$", t)]
                    tag_mask = np.any(self.tag_matrix[:, tag_matches], axis=1)
                else:
                    try:
                        tag_idx = self.unique_tags.index(condition['value'])
                        tag_mask = self.tag_matrix[:, tag_idx]
                    except ValueError:
                        tag_mask = np.zeros(self.size, dtype=bool)
                mask &= tag_mask

            elif condition['type'] == 'path':
                if '*' in condition['value']:
                    pattern = condition['value'].replace('*', '.*')
                    path_matches = [i for i, p in enumerate(self.unique_paths)
                                    if re.match(f"^{pattern}$", p)]
                    path_mask = np.any(self.path_matrix[:, path_matches], axis=1)
                else:
                    try:
                        path_idx = self.unique_paths.index(condition['value'])
                        path_mask = self.path_matrix[:, path_idx]
                    except ValueError:
                        path_mask = np.zeros(self.size, dtype=bool)
                mask &= path_mask

            elif condition['type'] == 'param':
                param = condition['field']
                if param in self.param_arrays:
                    values = self.param_arrays[param][:self.size]
                    op = condition['operator']
                    value = condition['value']

                    if op == '=':
                        param_mask = values == value
                    elif op == '>':
                        param_mask = values > value
                    elif op == '<':
                        param_mask = values < value
                    elif op == '>=':
                        param_mask = values >= value
                    elif op == '<=':
                        param_mask = values <= value

                    mask &= param_mask

        # Convert matches to result format
        results = []
        for idx in np.where(mask)[0]:
            result = {
                'block_id': self.block_ids[idx],
                'file_path': self.file_paths[idx],
                'content_start': int(self.content_starts[idx]),
                'content_end': int(self.content_ends[idx]) if self.content_ends[idx] is not None else None,
                'tags': [t for i, t in enumerate(self.unique_tags) if self.tag_matrix[idx, i]],
                'paths': [p for i, p in enumerate(self.unique_paths) if self.path_matrix[idx, i]],
                'parameters': {}
            }

            for key in self.param_arrays:
                if idx < len(self.param_arrays[key]):
                    result['parameters'][key] = self.param_arrays[key][idx]

            results.append(result)

        return results

def process_stream(stream: Iterator[str], store: BlockStore):
    """Process a stream of blocks and add to store"""
    # This would integrate with your existing StreamingParser
    # For each block from the parser:
    #     store.add_block(block.to_dict())
    # store.flush()
    pass