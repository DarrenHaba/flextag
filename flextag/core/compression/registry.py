from typing import Dict, Type
from ..interfaces.compressor import ICompressor
from flextag.exceptions import CompressionError
from flextag.logger import logger


class CompressionRegistry:
    """Registry for compression handlers"""
    _compressors: Dict[str, Type[ICompressor]] = {}

    @classmethod
    def register(cls, name: str, compressor: Type[ICompressor]) -> None:
        """Register a new compression handler"""
        cls._compressors[name] = compressor
        logger.debug(f"Registered compression handler: {name}")

    @classmethod
    def get(cls, name: str) -> ICompressor:
        """Get compression handler by name"""
        if name not in cls._compressors:
            logger.error(f"Unknown compression method: {name}")
            raise CompressionError(f"Unknown compression method: {name}")
        return cls._compressors[name]()

