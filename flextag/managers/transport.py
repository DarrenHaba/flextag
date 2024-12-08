from typing import Optional
from base import BaseManager
import logging

logger = logging.getLogger(__name__)


class TransportManager(BaseManager):
    """Manager for transport container operations"""

    def __init__(self):
        super().__init__("transport_manager")
        self.create_registry("encoders")
        self.create_registry("compressors")

        # Default settings
        self._default_encoding = "base64"
        self._default_compression = None

    def set_default_encoding(self, encoding: str) -> None:
        """Set default encoding method"""
        if encoding not in self.get_supported_encodings():
            raise ValueError(f"Unsupported encoding: {encoding}")
        self._default_encoding = encoding

    def set_default_compression(self, compression: Optional[str]) -> None:
        """Set default compression method"""
        if compression and compression not in self.get_supported_compression():
            raise ValueError(f"Unsupported compression: {compression}")
        self._default_compression = compression

    def get_supported_encodings(self) -> list[str]:
        """Get list of supported encoding methods"""
        return list(self._registries.get("encoders", {}).keys())

    def get_supported_compression(self) -> list[str]:
        """Get list of supported compression methods"""
        return list(self._registries.get("compressors", {}).keys())

    def encode(self, data: str, encoding: Optional[str] = None,
               compression: Optional[str] = None) -> str:
        """Encode data into transport format"""
        try:
            # Use specified or default values
            enc = encoding or self._default_encoding
            comp = compression or self._default_compression

            # Apply compression if specified
            if comp:
                compressor = self.get("compressors", comp)
                data = compressor.compress(data)

            # Apply encoding
            encoder = self.get("encoders", enc)
            result = encoder.encode(data)

            logger.debug(f"Encoded data with {enc} encoding and {comp or 'no'} compression")
            return result

        except Exception as e:
            logger.error(f"Failed to encode data: {str(e)}")
            raise

    def decode(self, data: str) -> str:
        """Decode data from transport format"""
        try:
            # Extract format info and data
            # TODO: Implement format detection and decoding
            raise NotImplementedError("Decode not yet implemented")

        except Exception as e:
            logger.error(f"Failed to decode data: {str(e)}")
            raise
