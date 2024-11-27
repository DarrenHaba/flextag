from typing import Protocol


class ICompressor(Protocol):
    """Interface for compression implementations"""

    def compress(self, data: str) -> bytes:
        """Compress string data to bytes"""
        ...

    def decompress(self, data: bytes) -> str:
        """Decompress bytes to string"""
        ...
