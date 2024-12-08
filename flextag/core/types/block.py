from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class DataBlock:
    """Represents a parsed data block with metadata and content information"""
    id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    paths: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    content_start: int = 0  # Line number where content starts
    content_end: Optional[int] = None  # Line number where content ends
    file_path: Optional[str] = None  # Source file path if applicable
    raw_content: Optional[str] = None  # Only populated when explicitly requested

    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary representation"""
        return {
            "id": self.id,
            "tags": self.tags,
            "paths": self.paths,
            "parameters": self.parameters,
            "content_start": self.content_start,
            "content_end": self.content_end,
            "file_path": self.file_path
        }
