from typing import Generator, Dict, Any, Iterator, Optional
import json
import logging
from pathlib import Path

from ..types.block import DataBlock

logger = logging.getLogger(__name__)


class StreamingParser:
    """Fast line-by-line parser for data blocks"""

    def __init__(self):
        self.DATA_START = "[[DATA"
        self.DATA_END = "[[/DATA]]"

    def parse_metadata(self, metadata_str: str) -> Dict[str, Any]:
        """Parse metadata string into structured fields."""
        result = {"id": None, "tags": [], "paths": [], "parameters": {}}
    
        # Find JSON by matching from first { to end
        json_start = metadata_str.find("{")
        if json_start != -1:
            try:
                json_str = metadata_str[json_start:]
                result["parameters"] = json.loads(json_str)
                metadata_str = metadata_str[:json_start].rstrip(" ,")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in metadata: {e}")
                raise
    
        # Split the remaining metadata into parts
        parts = metadata_str.split()
        for part in parts:
            if part.startswith(":"):  # ID
                result["id"] = part[1:]
            elif part.startswith("#"):  # Tags
                result["tags"].append(part[1:])
            elif part.startswith("."):  # Paths
                result["paths"].append(part[1:])
    
        return result

    def parse_stream(self, lines: Iterator[str], file_path: Optional[str] = None) -> Generator[DataBlock, None, None]:
        """Parse text stream line by line, yielding data blocks"""
        current_block = None
        line_number = 0

        for line in lines:
            line_number += 1
            line = line.strip()

            if not line:
                continue

            if line.startswith("["):
                if line.startswith(self.DATA_START):
                    # Handle self-closing tags
                    if line.endswith("/]]"):
                        meta_end = line.find("/]]")
                        metadata = line[6:meta_end]  # 6 is len('[[DATA')
                        parsed_meta = self.parse_metadata(metadata)

                        block = DataBlock(
                            id=parsed_meta["id"],
                            tags=parsed_meta["tags"],
                            paths=parsed_meta["paths"],
                            parameters=parsed_meta["parameters"],
                            content_start=line_number,
                            content_end=line_number,
                            file_path=file_path
                        )
                        yield block
                        continue

                    # Regular opening tag
                    meta_end = line.find("]]")
                    if meta_end != -1:
                        metadata = line[6:meta_end]  # 6 is len('[[DATA')
                        parsed_meta = self.parse_metadata(metadata)

                        current_block = DataBlock(
                            id=parsed_meta["id"],
                            tags=parsed_meta["tags"],
                            paths=parsed_meta["paths"],
                            parameters=parsed_meta["parameters"],
                            content_start=line_number + 1,
                            file_path=file_path
                        )

                elif line == self.DATA_END and current_block is not None:
                    current_block.content_end = line_number - 1
                    yield current_block
                    current_block = None

    def parse_string(self, content: str) -> Generator[DataBlock, None, None]:
        """Parse a string containing data blocks"""
        yield from self.parse_stream(iter(content.splitlines()))

    def parse_file(self, file_path: Path) -> Generator[DataBlock, None, None]:
        """Parse a file containing data blocks"""
        with open(file_path) as f:
            yield from self.parse_stream(f, str(file_path))
