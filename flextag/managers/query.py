from typing import Optional, List, Dict, Any
from pathlib import Path
from .base import BaseManager, ManagerEvent
import numpy as np
import logging
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

class QueryManager(BaseManager):
    """Optimized manager for query operations using NumPy"""

    BATCH_SIZE = 1000

    def __init__(self, db_path: Optional[Path] = None):
        super().__init__("query_manager")
    
        # Initialize empty arrays
        self.block_ids = np.array([], dtype=object)
        self.file_paths = np.array([], dtype=object)
        self.content_starts = np.array([], dtype=np.int32)
        self.content_ends = np.array([], dtype=object)
    
        # Tag and path matrices
        self.tag_matrix = None
        self.path_matrix = None
        self.unique_tags = []
        self.unique_paths = []
    
        # Parameter storage
        self.param_arrays = {}  # Typed parameter arrays
        self.param_objects = {}  # For non-vectorizable parameters
    
        # Batch processing
        self.pending_blocks = []
        self.BATCH_SIZE = 1000
    
        # Create registries
        self.create_registry("query_parsers")
    
        # Subscribe to block_parsed event
        self.subscribe("block_parsed", self.handle_block_parsed)
        logger.debug("Query manager initialized")

    def _init_arrays(self, size: int):
        """Initialize arrays with given size"""
        self.block_ids = np.empty(size, dtype=object)
        self.file_paths = np.empty(size, dtype=object)
        self.content_starts = np.zeros(size, dtype=np.int32)
        self.content_ends = np.empty(size, dtype=object)

        # Tag and path matrices
        self.tag_matrix = None
        self.path_matrix = None
        self.unique_tags = []
        self.unique_paths = []

        # Optimized parameter storage
        self.param_arrays = {}
        self.param_types = {}

    def _ensure_capacity(self, needed_size: int):
        """Ensure arrays have sufficient capacity"""
        if needed_size >= len(self.block_ids):  # Changed from > to >=
            new_size = max(needed_size + self.BATCH_SIZE, len(self.block_ids) * 2)

            # Create new arrays with larger size
            new_block_ids = np.empty(new_size, dtype=object)
            new_file_paths = np.empty(new_size, dtype=object)
            new_content_starts = np.zeros(new_size, dtype=np.int32)
            new_content_ends = np.empty(new_size, dtype=object)

            # Copy existing data
            new_block_ids[:self.current_size] = self.block_ids[:self.current_size]
            new_file_paths[:self.current_size] = self.file_paths[:self.current_size]
            new_content_starts[:self.current_size] = self.content_starts[:self.current_size]
            new_content_ends[:self.current_size] = self.content_ends[:self.current_size]

            # Update references
            self.block_ids = new_block_ids
            self.file_paths = new_file_paths
            self.content_starts = new_content_starts
            self.content_ends = new_content_ends

            # Resize matrices if they exist
            if self.tag_matrix is not None:
                new_tag_matrix = np.zeros((new_size, self.tag_matrix.shape[1]), dtype=bool)
                new_tag_matrix[:self.current_size] = self.tag_matrix[:self.current_size]
                self.tag_matrix = new_tag_matrix

            if self.path_matrix is not None:
                new_path_matrix = np.zeros((new_size, self.path_matrix.shape[1]), dtype=bool)
                new_path_matrix[:self.current_size] = self.path_matrix[:self.current_size]
                self.path_matrix = new_path_matrix

            # Resize parameter arrays
            for key in list(self.param_arrays.keys()):
                old_array = self.param_arrays[key]
                new_array = np.empty(new_size, dtype=old_array.dtype)
                new_array[:self.current_size] = old_array[:self.current_size]
                self.param_arrays[key] = new_array

    def _process_batch(self):
        """Process a batch of pending blocks"""
        if not self.pending_blocks:
            return
    
        current_size = len(self.block_ids)
        new_size = current_size + len(self.pending_blocks)
    
        # Update core arrays
        self.block_ids = np.append(self.block_ids, [b['id'] for b in self.pending_blocks])
        self.file_paths = np.append(self.file_paths, [b['file_path'] for b in self.pending_blocks])
        self.content_starts = np.append(self.content_starts, [b['content_start'] for b in self.pending_blocks])
        self.content_ends = np.append(self.content_ends, [b['content_end'] for b in self.pending_blocks])
    
        # Collect all new tags and paths
        new_tags = set()
        new_paths = set()
        for block in self.pending_blocks:
            new_tags.update(block['tags'])
            new_paths.update(block['paths'])
    
        # Update tag matrix
        if new_tags - set(self.unique_tags):
            self.unique_tags.extend(sorted(new_tags - set(self.unique_tags)))
            new_tag_matrix = np.zeros((new_size, len(self.unique_tags)), dtype=bool)
            if self.tag_matrix is not None:
                new_tag_matrix[:current_size, :self.tag_matrix.shape[1]] = self.tag_matrix
            self.tag_matrix = new_tag_matrix
    
        # Update path matrix
        if new_paths - set(self.unique_paths):
            self.unique_paths.extend(sorted(new_paths - set(self.unique_paths)))
            new_path_matrix = np.zeros((new_size, len(self.unique_paths)), dtype=bool)
            if self.path_matrix is not None:
                new_path_matrix[:current_size, :self.path_matrix.shape[1]] = self.path_matrix
            self.path_matrix = new_path_matrix
    
        # Set values for new blocks
        for i, block in enumerate(self.pending_blocks, current_size):
            # Set tags
            for tag in block['tags']:
                tag_idx = self.unique_tags.index(tag)
                self.tag_matrix[i, tag_idx] = True
    
            # Set paths
            for path in block['paths']:
                path_idx = self.unique_paths.index(path)
                self.path_matrix[i, path_idx] = True
    
            # Handle parameters
            for key, value in block['parameters'].items():
                if isinstance(value, (int, float, bool)):
                    if key not in self.param_arrays:
                        self.param_arrays[key] = np.array([None] * current_size, dtype=type(value))
                        self.param_arrays[key] = np.append(self.param_arrays[key], [None] * len(self.pending_blocks))
                    self.param_arrays[key][i] = value
                else:
                    if key not in self.param_objects:
                        self.param_objects[key] = {}
                    self.param_objects[key][i] = value
    
        # Clear pending blocks
        self.pending_blocks = []

    def flush(self):
        """Process any remaining pending blocks"""
        if self.pending_blocks:
            self._process_batch()

    def handle_block_parsed(self, event: ManagerEvent) -> None:
        """Queue blocks for batch processing"""
        try:
            if event.event_type != "block_parsed":
                return
    
            block = event.data["block"]
            file_path = event.data.get("file")
    
            # Add to pending blocks
            self.pending_blocks.append({
                'id': block.id,
                'tags': block.tags,
                'paths': block.paths,
                'parameters': block.parameters,
                'content_start': block.content_start,
                'content_end': block.content_end,
                'file_path': file_path
            })
    
            # Process batch if we've reached batch size
            if len(self.pending_blocks) >= self.BATCH_SIZE:
                self._process_batch()
    
        except Exception as e:
            logger.error(f"Error handling block_parsed event: {str(e)}")
            raise

    def _get_pattern(self, pattern: str) -> re.Pattern:
        """Get or create compiled regex pattern"""
        if pattern not in self.pattern_cache:
            self.pattern_cache[pattern] = re.compile(f"^{pattern.replace('*', '.*')}$")
        return self.pattern_cache[pattern]

    def validate_query(self, query: str) -> None:
        """Validate query format before processing"""
        parts = query.split(' AND ')
        for part in parts:
            part = part.strip()
    
            # Each part must be either a tag, path, or parameter condition
            if not (part.startswith('#') or part.startswith('.') or ' = ' in part):
                raise ValueError(f"Invalid query format: '{part}'. Must start with '#' for tags, '.' for paths, or contain ' = ' for parameters")
    
            # Parameter validation
            if ' = ' in part:
                if part.count('=') > 1:
                    raise ValueError(f"Invalid parameter format: '{part}'. Only one '=' allowed")
                if ':' in part:
                    raise ValueError(f"Invalid parameter format: '{part}'. Use '=' instead of ':'")
                field, value = [x.strip() for x in part.split(' = ')]
                if not field:
                    raise ValueError("Parameter name cannot be empty")
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Execute search query"""
        try:
            # Validate query format
            self.validate_query(query)
    
            # Ensure any pending blocks are processed
            self.flush()
    
            if len(self.block_ids) == 0:
                return []

    
            conditions = query.split(' AND ')
            mask = np.ones(len(self.block_ids), dtype=bool)
    
            for condition in conditions:
                condition = condition.strip()
    
                # Tag search
                if condition.startswith('#'):
                    tag = condition[1:]
                    if '*' in tag:
                        pattern = tag.replace('*', '.*')
                        tag_matches = [i for i, t in enumerate(self.unique_tags)
                                       if re.match(f"^{pattern}$", t, re.IGNORECASE)]
                        if tag_matches:
                            tag_mask = np.any(self.tag_matrix[:, tag_matches], axis=1)
                        else:
                            tag_mask = np.zeros(len(self.block_ids), dtype=bool)
                    else:
                        try:
                            # Case-insensitive tag matching
                            tag_idx = next(i for i, t in enumerate(self.unique_tags)
                                           if t.lower() == tag.lower())
                            tag_mask = self.tag_matrix[:, tag_idx]
                        except StopIteration:
                            tag_mask = np.zeros(len(self.block_ids), dtype=bool)
                    mask &= tag_mask
    
                # Path search
                elif condition.startswith('.'):
                    path = condition[1:]
                    if '*' in path:
                        pattern = path.replace('*', '.*')
                        path_matches = [i for i, p in enumerate(self.unique_paths)
                                        if re.match(f"^{pattern}$", p, re.IGNORECASE)]
                        if path_matches:
                            path_mask = np.any(self.path_matrix[:, path_matches], axis=1)
                        else:
                            path_mask = np.zeros(len(self.block_ids), dtype=bool)
                    else:
                        try:
                            # Case-insensitive path matching
                            path_idx = next(i for i, p in enumerate(self.unique_paths)
                                            if p.lower() == path.lower())
                            path_mask = self.path_matrix[:, path_idx]
                        except StopIteration:
                            path_mask = np.zeros(len(self.block_ids), dtype=bool)
                    mask &= path_mask
    
                # Parameter search
                elif ' = ' in condition:
                    field, value = [x.strip() for x in condition.split(' = ')]
    
                    # Remove quotes from string values
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
    
                    param_mask = np.zeros(len(self.block_ids), dtype=bool)
    
                    # Check param_arrays first
                    if field in self.param_arrays:
                        param_array = self.param_arrays[field]
                        try:
                            if any(isinstance(x, bool) for x in param_array):
                                param_value = value.lower() == 'true'
                            elif any(isinstance(x, int) for x in param_array):
                                param_value = int(value)
                            elif any(isinstance(x, float) for x in param_array):
                                param_value = float(value)
                            else:
                                param_value = value
    
                            param_mask = param_array == param_value
                        except (ValueError, TypeError):
                            # If conversion fails, treat as string comparison
                            param_mask = np.array([str(x).lower() == value.lower()
                                                   if x is not None else False
                                                   for x in param_array])
    
                    # Then check param_objects
                    if field in self.param_objects:
                        for idx, stored_value in self.param_objects[field].items():
                            if str(stored_value).lower() == value.lower():
                                param_mask[idx] = True
    
                    mask &= param_mask
    
                else:
                    raise ValueError(f"Invalid query condition: {condition}")
    
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
    
                # Add parameters
                for key, array in self.param_arrays.items():
                    if idx < len(array):
                        result['parameters'][key] = array[idx]
                for key, obj_dict in self.param_objects.items():
                    if idx in obj_dict:
                        result['parameters'][key] = obj_dict[idx]
    
                results.append(result)
    
            return results
    
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise