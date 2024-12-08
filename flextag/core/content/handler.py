from pathlib import Path
from typing import Optional, Tuple, Dict, TextIO
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ContentHandler:
    """Handles lazy loading and caching of block content"""

    def __init__(self):
        self._file_handles: Dict[str, TextIO] = {}
        self._content_cache = {}

    @contextmanager
    def _get_file_handle(self, file_path: str):
        """Get or create file handle with context management"""
        if file_path not in self._file_handles:
            self._file_handles[file_path] = open(file_path, 'r')

        try:
            yield self._file_handles[file_path]
        finally:
            # Don't close here - we'll reuse the handle
            pass

    def close_all(self):
        """Close all open file handles"""
        for handle in self._file_handles.values():
            handle.close()
        self._file_handles.clear()

    def get_content(self, block_id: str, file_path: Path, line_range: tuple[int, int]) -> str:
        """Get content for a block by line range"""
        cache_key = f"{file_path}:{block_id}"

        # Check cache first
        if cache_key in self._content_cache:
            return self._content_cache[cache_key]

        try:
            content_lines = []
            start_line, end_line = line_range

            file_key = str(file_path)
            if file_key not in self._file_handles:
                self._file_handles[file_key] = open(file_path, 'r')

            f = self._file_handles[file_key]

            # Reset file position
            f.seek(0)

            current_line = 0
            for line in f:
                current_line += 1
                if current_line < start_line:
                    continue
                if current_line > end_line:
                    break
                content_lines.append(line.rstrip('\n'))

            content = '\n'.join(content_lines)

            # Cache the content
            self._content_cache[cache_key] = content
            return content

        except Exception as e:
            self.close()  # Close handles on error
            raise

    def close(self) -> None:
        """Close all open file handles"""
        for handle in self._file_handles.values():
            try:
                handle.close()
            except Exception:
                pass  # Ignore errors during cleanup
        self._file_handles.clear()

    def __del__(self):
        """Ensure file handles are closed"""
        self.close()
