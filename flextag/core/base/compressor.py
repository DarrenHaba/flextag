from abc import ABC
from ..interfaces.compressor import ICompressor


class BaseCompressor(ABC, ICompressor):
    """Base implementation of compression handler"""

    def compress(self, data: str) -> bytes:
        raise NotImplementedError

    def decompress(self, data: bytes) -> str:
        raise NotImplementedError
