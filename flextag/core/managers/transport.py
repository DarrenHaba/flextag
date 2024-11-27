from typing import Dict, Optional, Type
from flextag.core.interfaces.managers import ITransportManager
from flextag.core.interfaces.transport import (
    ICompressor,
    IEncoder,
    ITransportContainer,
    EncodingType
)
from flextag.core.types.container import Container
from flextag.logger import logger
from flextag.exceptions import TransportError


class TransportManager(ITransportManager):
    """Manager for transport operations"""

    def __init__(self):
        self._compressors: Dict[str, Type[ICompressor]] = {}
        self._encoders: Dict[str, Type[IEncoder]] = {}
        self._transport_container: Optional[ITransportContainer] = None
        self._default_encoding: EncodingType = "base64"
        self._default_compression: str = ""
        logger.debug("Initialized TransportManager")

    def register_compressor(self, name: str, compressor: Type[ICompressor]) -> None:
        """Register compression implementation"""
        try:
            self._compressors[name] = compressor
            logger.debug(f"Registered compressor: {name}")
        except Exception as e:
            logger.error(f"Failed to register compressor: {str(e)}", name=name)
            raise TransportError(
                f"Failed to register compressor '{name}': {str(e)}"
            )

    def register_encoder(self, name: str, encoder: Type[IEncoder]) -> None:
        """Register encoder implementation"""
        try:
            self._encoders[name] = encoder
            logger.debug(f"Registered encoder: {name}")
        except Exception as e:
            logger.error(f"Failed to register encoder: {str(e)}", name=name)
            raise TransportError(
                f"Failed to register encoder '{name}': {str(e)}"
            )

    def register_transport_container(
            self,
            container: Type[ITransportContainer]
    ) -> None:
        """Register transport container implementation"""
        self._transport_container = container()
        logger.debug("Registered transport container")

    def set_default_encoding(self, encoding: EncodingType) -> None:
        """Set default encoding type"""
        if encoding not in ("base64", "base32", "base16"):
            raise TransportError(f"Invalid encoding type: {encoding}")

        self._default_encoding = encoding
        logger.debug(f"Set default encoding to: {encoding}")

    def set_default_compression(self, compression: str) -> None:
        """Set default compression algorithm"""
        if compression and compression not in self._compressors:
            raise TransportError(f"Compression '{compression}' not registered")

        self._default_compression = compression
        logger.debug(f"Set default compression to: {compression}")

    def to_transport(
            self,
            container: Container,
            encoding: Optional[str] = None,
            compression: Optional[str] = None
    ) -> str:
        """Convert container to transport format"""
        try:
            if not self._transport_container:
                raise TransportError("No transport container registered")

            # Use specified or default values
            enc = encoding or self._default_encoding
            comp = compression or self._default_compression

            # Configure transport container
            self._transport_container.set_encoding(enc)
            if comp:
                self._transport_container.set_compression(comp)

            # Convert to transport format
            result = self._transport_container.encode(container)

            logger.debug(
                f"Converted container to transport format "
                f"(encoding={enc}, compression={comp or 'none'})"
            )
            return result

        except Exception as e:
            logger.error(f"Transport encoding failed: {str(e)}")
            raise TransportError(f"Transport encoding failed: {str(e)}")

    def from_transport(self, transport: str) -> Container:
        """Convert transport format back to container"""
        try:
            if not self._transport_container:
                raise TransportError("No transport container registered")

            container = self._transport_container.decode(transport)

            logger.debug("Converted transport format back to container")
            return container

        except Exception as e:
            logger.error(f"Transport decoding failed: {str(e)}")
            raise TransportError(f"Transport decoding failed: {str(e)}")
