import gzip
import zipfile
from io import BytesIO
from typing import Protocol, Dict, Type
from flextag.logger import logger


class Compressor(Protocol):
    """Interface for compression handlers"""
    def compress(self, data: str) -> bytes:
        ...

    def decompress(self, data: bytes) -> str:
        ...


class GzipCompressor:
    """Gzip compression handler"""
    def compress(self, data: str) -> bytes:
        return gzip.compress(data.encode())

    def decompress(self, data: bytes) -> str:
        return gzip.decompress(data).decode()


class ZipCompressor:
    """Zip compression handler"""
    def compress(self, data: str) -> bytes:
        bio = BytesIO()
        with zipfile.ZipFile(bio, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('data', data)
        return bio.getvalue()

    def decompress(self, data: bytes) -> str:
        bio = BytesIO(data)
        with zipfile.ZipFile(bio, 'r') as zf:
            return zf.read('data').decode()


class CompressionRegistry:
    """Registry for compression handlers"""
    _compressors: Dict[str, Type[Compressor]] = {
        'gzip': GzipCompressor,
        'zip': ZipCompressor
    }

    @classmethod
    def get_compressor(cls, name: str) -> Compressor:
        """Get compression handler by name"""
        if name not in cls._compressors:
            raise ValueError(f"Unknown compression method: {name}")
        return cls._compressors[name]()

    @classmethod
    def register_compressor(cls, name: str, compressor: Type[Compressor]):
        """Register new compression handler"""
        cls._compressors[name] = compressor
        logger.debug(f"Registered compression handler: {name}")
