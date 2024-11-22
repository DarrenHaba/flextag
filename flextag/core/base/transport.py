from abc import ABC
from typing import Dict, Any
import json
import base64

from ..compression import CompressionRegistry
from ..interfaces.transport import ITransportContainer
from ..interfaces.container import IContainer
from flextag.exceptions import TransportError
from flextag.logger import logger
from flextag.settings import Const


class BaseTransportContainer(ABC, ITransportContainer):
    """Base implementation of transport container with encoding/decoding logic"""

    def __init__(self):
        self.metadata: Dict[str, Any] = {
            "compression": "",
            "encryption": "",
            "encoding": "base64",
            "version": "1.0",
            "checksum": "",
            "created": ""
        }
        logger.debug("Initialized transport container")

    def _encode_metadata(self) -> str:
        """Encode metadata to transport format"""
        try:
            return base64.b64encode(json.dumps(self.metadata).encode()).decode()
        except Exception as e:
            logger.error(f"Metadata encoding error: {str(e)}")
            raise TransportError("Failed to encode metadata")

    def _decode_metadata(self, data: str) -> Dict[str, Any]:
        """Decode metadata from transport format"""
        try:
            return json.loads(base64.b64decode(data).decode())
        except Exception as e:
            logger.error(f"Metadata decoding error: {str(e)}")
            raise TransportError("Failed to decode metadata")

    def _encode_data(self, data: str) -> str:
        """Encode data with optional compression and encryption"""
        try:
            # Apply compression if specified
            if self.metadata["compression"]:
                try:
                    compressor = CompressionRegistry.get_compressor(self.metadata["compression"])
                    data = compressor.compress(data)
                except Exception as e:
                    logger.error(f"Compression error: {str(e)}")
                    raise TransportError(f"Compression failed: {str(e)}")

            # Apply encryption if specified
            if self.metadata["encryption"]:
                # Add encryption logic here
                pass

            # Always base64 encode
            return base64.b64encode(data.encode()).decode()
        except Exception as e:
            logger.error(f"Data encoding error: {str(e)}")
            raise TransportError("Failed to encode data")

    def _decode_data(self, data: str) -> str:
        """Decode data with optional decompression and decryption"""
        try:
            # Base64 decode
            decoded = base64.b64decode(data).decode()

            # Apply decryption if specified
            if self.metadata["encryption"]:
                # Add decryption logic here
                pass

            # Apply decompression if specified
            if self.metadata["compression"]:
                try:
                    compressor = CompressionRegistry.get_compressor(self.metadata["compression"])
                    decoded = compressor.decompress(decoded)
                except Exception as e:
                    logger.error(f"Decompression error: {str(e)}")
                    raise TransportError(f"Decompression failed: {str(e)}")

            return decoded
        except Exception as e:
            logger.error(f"Data decoding error: {str(e)}")
            raise TransportError("Failed to decode data")
