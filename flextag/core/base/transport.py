from abc import ABC
from typing import Dict, Any
import json
import base64

from ..compression.registry import CompressionRegistry
from ..interfaces.transport import ITransportContainer
from ...exceptions import TransportError
from ...logger import logger


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
            # Start with string data
            current_data = data.encode()  # Convert to bytes first
    
            # Apply compression if specified
            if self.metadata["compression"]:
                try:
                    compressor = CompressionRegistry.get(self.metadata["compression"])
                    current_data = compressor.compress(data)  # Returns bytes
                except Exception as e:
                    logger.error(f"Compression error: {str(e)}")
                    raise TransportError(f"Compression failed: {str(e)}")
    
            # Base64 encode the final bytes
            return base64.b64encode(current_data).decode()
    
        except Exception as e:
            logger.error(f"Data encoding error: {str(e)}")
            raise TransportError(f"Failed to encode data: {str(e)}")
    
    def _decode_data(self, data: str) -> str:
        """Decode data with optional decompression and decryption"""
        try:
            # Base64 decode first
            current_data = base64.b64decode(data)  # Returns bytes
    
            # Apply decompression if specified
            if self.metadata["compression"]:
                try:
                    compressor = CompressionRegistry.get(self.metadata["compression"])
                    current_data = compressor.decompress(current_data)  # Returns str
                except Exception as e:
                    logger.error(f"Decompression error: {str(e)}")
                    raise TransportError(f"Decompression failed: {str(e)}")
            else:
                # If no compression was used, decode the bytes to string
                current_data = current_data.decode()
    
            return current_data
    
        except Exception as e:
            logger.error(f"Data decoding error: {str(e)}")
            raise TransportError(f"Failed to decode data: {str(e)}")
