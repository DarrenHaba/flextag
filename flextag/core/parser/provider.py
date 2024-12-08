from pathlib import Path
from typing import Generator, Optional

from ...core.parser.streaming import StreamingParser
from ..types.block import DataBlock


class ParserProvider:
    """Provider class for streaming parser"""

    def __init__(self):
        self._parser = StreamingParser()

    def parse_stream(self, lines, file_path: Optional[str] = None) -> Generator[DataBlock, None, None]:
        """Pass through to streaming parser's parse_stream"""
        return self._parser.parse_stream(lines, file_path)

    def parse_string(self, content: str) -> Generator[DataBlock, None, None]:
        """Parse a string containing data blocks"""
        return self._parser.parse_stream(iter(content.splitlines()))

    def parse_file(self, file_path: Path) -> Generator[DataBlock, None, None]:
        """Parse a file containing data blocks"""
        with open(file_path) as f:
            yield from self._parser.parse_stream(f, str(file_path))
