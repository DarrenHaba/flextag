import base64
from flextag.core.interfaces.transport import IEncoder
from flextag.logger import logger
from flextag.exceptions import FlexTagError


class Base64Encoder(IEncoder):
    """Base64 encoding implementation"""

    def encode(self, data: bytes) -> str:
        """Encode bytes to base64 string"""
        try:
            return base64.b64encode(data).decode()
        except Exception as e:
            logger.error(f"Base64 encoding failed: {str(e)}")
            raise FlexTagError(f"Base64 encoding failed: {str(e)}")

    def decode(self, data: str) -> bytes:
        """Decode base64 string to bytes"""
        try:
            return base64.b64decode(data.encode())
        except Exception as e:
            logger.error(f"Base64 decoding failed: {str(e)}")
            raise FlexTagError(f"Base64 decoding failed: {str(e)}")


class Base32Encoder(IEncoder):
    """Base32 encoding implementation"""

    def encode(self, data: bytes) -> str:
        """Encode bytes to base32 string"""
        try:
            return base64.b32encode(data).decode()
        except Exception as e:
            logger.error(f"Base32 encoding failed: {str(e)}")
            raise FlexTagError(f"Base32 encoding failed: {str(e)}")

    def decode(self, data: str) -> bytes:
        """Decode base32 string to bytes"""
        try:
            return base64.b32decode(data.encode())
        except Exception as e:
            logger.error(f"Base32 decoding failed: {str(e)}")
            raise FlexTagError(f"Base32 decoding failed: {str(e)}")


class Base16Encoder(IEncoder):
    """Base16 encoding implementation"""

    def encode(self, data: bytes) -> str:
        """Encode bytes to base16 string"""
        try:
            return base64.b16encode(data).decode()
        except Exception as e:
            logger.error(f"Base16 encoding failed: {str(e)}")
            raise FlexTagError(f"Base16 encoding failed: {str(e)}")

    def decode(self, data: str) -> bytes:
        """Decode base16 string to bytes"""
        try:
            return base64.b16decode(data.encode())
        except Exception as e:
            logger.error(f"Base16 decoding failed: {str(e)}")
            raise FlexTagError(f"Base16 decoding failed: {str(e)}")


# Register default encoders
def register_default_encoders():
    """Register default encoding implementations"""
    try:
        from flextag.core.registry import Registries

        # Register encoders
        Registries.ENCODERS.register("base64", Base64Encoder())
        Registries.ENCODERS.register("base32", Base32Encoder())
        Registries.ENCODERS.register("base16", Base16Encoder())

        # Set base64 as default
        Registries.ENCODERS.set_active("base64")

        logger.debug("Registered default encoders")

    except Exception as e:
        logger.error(f"Failed to register default encoders: {str(e)}")
        raise FlexTagError(f"Failed to register default encoders: {str(e)}")


# Auto-register on import
register_default_encoders()
