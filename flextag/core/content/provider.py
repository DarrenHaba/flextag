from pathlib import Path
from typing import Optional, Tuple

from ...core.content.handler import ContentHandler


class ContentProvider:
    """Provider class for registering with manager"""

    def __init__(self):
        self._handler = ContentHandler()

    def get_content(
            self,
            block_id: str,
            line_range: Tuple[int, int],
            file_path: Optional[str] = None
    ) -> str:
        """Get content for a block
        
        Args:
            block_id: ID of the block
            line_range: Tuple of (start_line, end_line)
            file_path: Optional file path for file-based content
        """
        if not line_range:
            raise ValueError("Line range required")

        if file_path:
            return self._handler.get_content(block_id, Path(file_path), line_range)

        # For string-based content (no file)
        # This would need to be implemented differently or raise an error
        # depending on your requirements
        raise NotImplementedError("String-based content not yet implemented")

    def close(self):
        """Clean up resources"""
        self._handler.close()
