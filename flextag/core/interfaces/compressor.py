from typing import Protocol


class ICompressor(Protocol):
    """Interface for compression handlers"""
    def compress(self, data: str) -> bytes: ...
    def decompress(self, data: bytes) -> str: ...
