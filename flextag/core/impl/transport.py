from datetime import datetime
import hashlib
from ..base.transport import BaseTransportContainer
from ..interfaces.container import IContainer
from flextag.exceptions import TransportError
from flextag.logger import logger
from flextag.settings import Const


class TransportContainer(BaseTransportContainer):
    """Concrete implementation of transport container"""

    def encode(self, container: IContainer) -> str:
        """Convert data container to transport format"""
        try:
            # Update metadata
            self.metadata["created"] = datetime.now().isoformat()

            # Convert container to string
            data = container.to_string()

            # Calculate checksum
            self.metadata["checksum"] = hashlib.sha256(data.encode()).hexdigest()

            # Encode metadata and data
            meta_encoded = self._encode_metadata()
            data_encoded = self._encode_data(data)

            # Combine into transport format
            transport = f"{Const.TRANSPORT_START}{meta_encoded}{Const.TRANSPORT_DATA}{data_encoded}{Const.TRANSPORT_END}"

            logger.debug("Successfully encoded container to transport format")
            return transport

        except Exception as e:
            logger.error(f"Transport encoding error: {str(e)}")
            raise TransportError("Failed to create transport container")

    @classmethod
    def decode(cls, transport: str) -> IContainer:
        """Convert transport format back to data container"""
        try:
            # Validate format
            if not (transport.startswith(Const.TRANSPORT_START) and
                    transport.endswith(Const.TRANSPORT_END)):
                raise TransportError("Invalid transport container format")

            # Split metadata and data
            content = transport[len(Const.TRANSPORT_START):-len(Const.TRANSPORT_END)]
            meta_str, data_str = content.split(Const.TRANSPORT_DATA)

            # Create instance and decode
            instance = cls()
            instance.metadata = instance._decode_metadata(meta_str)
            data = instance._decode_data(data_str)

            # Verify checksum
            if instance.metadata["checksum"] != hashlib.sha256(data.encode()).hexdigest():
                raise TransportError("Checksum verification failed")

            # Parse data back to container
            from .container import Container  # Import here to avoid circular dependency
            container = Container.from_string(data)

            logger.debug("Successfully decoded transport container")
            return container

        except Exception as e:
            logger.error(f"Transport decoding error: {str(e)}")
            raise TransportError("Failed to decode transport container")
