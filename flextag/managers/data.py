from typing import Optional
from pathlib import Path
from .base import BaseManager
import logging

logger = logging.getLogger(__name__)


class DataManager(BaseManager):
    """Manager for data container operations"""

    def __init__(self):
        super().__init__("data_manager")
        self.create_registry("parsers")
        self.create_registry("content_handlers")

    def parse_file(self, file_path: Path) -> None:
        """Parse a .flextag file"""
        try:
            parser = self.get("parsers", "default")
            with open(file_path) as f:
                for block in parser.parse_stream(f):
                    self.emit("block_parsed", {
                        "file": str(file_path),
                        "block": block
                    })
            logger.debug(f"Parsed file: {file_path}")

        except Exception as e:
            logger.error(f"Failed to parse file: {str(e)}")
            raise

    def parse_string(self, content: str) -> None:
        """Parse a string containing data blocks"""
        try:
            parser = self.get("parsers", "default")
            for block in parser.parse_stream(content.splitlines()):
                # print(f"DEBUG: About to emit block: {block}")  # Debug line
                self.emit("block_parsed", {
                    "block": block
                })
            logger.debug("Parsed string content")

        except Exception as e:
            logger.error(f"Failed to parse string: {str(e)}")
            raise

    def get_content(self, block_id: str, content_range: tuple[int, int], file_path: Optional[str] = None) -> str:
        """Get content from a data block

        Args:
            block_id: ID of the block to get content from
            content_range: Tuple of (start_line, end_line)
            file_path: Optional file path (needed for file-based content)
        """
        try:
            handler = self.get("content_handlers", "default")
            content = handler.get_content(
                block_id=block_id,
                file_path=file_path,
                line_range=content_range
            )
            logger.debug(f"Retrieved content for block: {block_id}")
            return content

        except Exception as e:
            logger.error(f"Failed to get content: {str(e)}")
        raise
