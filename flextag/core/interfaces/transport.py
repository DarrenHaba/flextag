from typing import Protocol, Literal
from flextag.core.types.container import Container

EncodingType = Literal["base64", "base32", "base16"]

class IEncoder(Protocol):
    """Interface for data encoding"""

    def encode(self, data: bytes) -> str:
        """Encode bytes to string"""
        ...

    def decode(self, data: str) -> bytes:
        """Decode string to bytes"""
        ...


class ICompressor(Protocol):
    """Interface for data compression"""

    def compress(self, data: str) -> bytes:
        """Compress string to bytes"""
        ...

    def decompress(self, data: bytes) -> str:
        """Decompress bytes to string"""
        ...


class ITransportContainer(Protocol):
    """Interface for transport containers"""

    def set_encoding(self, encoding: EncodingType) -> None:
        """Set encoding type (base64, base32, base16)"""
        ...

    def set_compression(self, compression: str) -> None:
        """Set compression algorithm"""
        ...

    def encode(self, container: Container) -> str:
        """Convert data container to transport format"""
        ...

    def decode(self, transport: str) -> Container:
        """Convert transport format back to container"""
        ...
