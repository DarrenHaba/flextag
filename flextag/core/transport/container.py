from typing import Dict, Any
import json
import base64
from datetime import datetime
import hashlib

from flextag.core.interfaces.transport import ITransportContainer, EncodingType
from flextag.core.types.container import Container
from flextag.core.parsers.parsers import ContainerParser
from flextag.core.compression.registry import CompressionRegistry
from flextag.logger import logger
from flextag.exceptions import TransportError
from flextag.settings import Const


class TransportContainer(ITransportContainer):
    """Implementation of transport container format"""

    def __init__(self):
        self.metadata: Dict[str, Any] = {
            "compression": "",        # Compression method used
            "encryption": "",         # Encryption method used (future)
            "encoding": "base64",     # Encoding format (base64/base32/base16)
            "version": "1.0",         # Transport format version
            "checksum": "",          # Data checksum
            "created": "",           # Creation timestamp
        }
        self._parser = ContainerParser()

    def set_encoding(self, encoding: EncodingType) -> None:
        """Set encoding type"""
        if encoding not in ("base64", "base32", "base16"):
            raise TransportError(f"Invalid encoding type: {encoding}")
        self.metadata["encoding"] = encoding

    def set_compression(self, compression: str) -> None:
        """Set compression algorithm"""
        if compression and compression not in CompressionRegistry.list_compressors():
            raise TransportError(f"Compression '{compression}' not registered")
        self.metadata["compression"] = compression

    def encode(self, container: Container) -> str:
        """Convert data container to transport format"""
        try:
            # Update metadata
            self.metadata["created"] = datetime.now().isoformat()

            # Convert container to string
            data = self._parser.dump(container)

            # Apply compression if specified
            if self.metadata["compression"]:
                compressor = CompressionRegistry.get(self.metadata["compression"])
                data = compressor.compress(data)
                if isinstance(data, str):
                    data = data.encode()
            else:
                data = data.encode()

            # Calculate checksum
            self.metadata["checksum"] = hashlib.sha256(data).hexdigest()

            # Encode data based on specified encoding
            if self.metadata["encoding"] == "base64":
                encoded_data = base64.b64encode(data).decode()
            elif self.metadata["encoding"] == "base32":
                encoded_data = base64.b32encode(data).decode()
            else:  # base16
                encoded_data = base64.b16encode(data).decode()

            # Encode metadata
            encoded_meta = base64.b64encode(
                json.dumps(self.metadata).encode()
            ).decode()

            # Combine into transport format
            transport = (
                f"{Const.TRANSPORT_START}"
                f"{Const.TRANSPORT_META}{encoded_meta}"
                f"{Const.TRANSPORT_DATA}{encoded_data}"
                f"{Const.TRANSPORT_END}"
            )

            logger.debug(
                f"Created transport container: "
                f"compression={self.metadata['compression']}, "
                f"encoding={self.metadata['encoding']}"
            )
            return transport

        except Exception as e:
            logger.error(f"Transport encoding failed: {str(e)}")
            raise TransportError(f"Failed to create transport container: {str(e)}")

    def decode(self, transport: str) -> Container:
        """Convert transport format back to container"""
        try:
            # Validate format
            if not (
                    transport.startswith(Const.TRANSPORT_START) and
                    transport.endswith(Const.TRANSPORT_END)
            ):
                raise TransportError("Invalid transport container format")

            # Extract content
            content = transport[
                      len(Const.TRANSPORT_START):-len(Const.TRANSPORT_END)
                      ]

            # Split metadata and data
            meta_marker = Const.TRANSPORT_META
            data_marker = Const.TRANSPORT_DATA

            meta_start = content.index(meta_marker) + len(meta_marker)
            data_start = content.index(data_marker) + len(data_marker)

            meta_content = content[meta_start:content.index(data_marker)]
            data_content = content[data_start:]

            # Decode metadata
            self.metadata = json.loads(base64.b64decode(meta_content).decode())

            # Decode data based on encoding
            if self.metadata["encoding"] == "base64":
                decoded_data = base64.b64decode(data_content)
            elif self.metadata["encoding"] == "base32":
                decoded_data = base64.b32decode(data_content)
            else:  # base16
                decoded_data = base64.b16decode(data_content)

            # Apply decompression if needed
            if self.metadata["compression"]:
                compressor = CompressionRegistry.get(self.metadata["compression"])
                decoded_data = compressor.decompress(decoded_data)
            else:
                decoded_data = decoded_data.decode()

            # Verify checksum
            if self.metadata["checksum"] != hashlib.sha256(
                    decoded_data.encode()
            ).hexdigest():
                raise TransportError("Checksum verification failed")

            # Parse back to container
            container = self._parser.parse(decoded_data)

            logger.debug(
                f"Decoded transport container: "
                f"compression={self.metadata['compression']}, "
                f"encoding={self.metadata['encoding']}"
            )
            return container

        except Exception as e:
            logger.error(f"Transport decoding failed: {str(e)}")
            raise TransportError(f"Failed to decode transport container: {str(e)}")
