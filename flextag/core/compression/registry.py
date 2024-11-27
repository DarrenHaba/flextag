from typing import Dict, Type
from flextag.core.interfaces.compression import ICompressor
from flextag.core.compression.comp_gzip import GzipCompressor
from flextag.core.compression.comp_zip import ZipCompressor
from flextag.logger import logger
from flextag.exceptions import CompressionError


class CompressionRegistry:
    """Registry for compression implementations"""

    _compressors: Dict[str, ICompressor] = {}
    _active_compressor: str = ""

    @classmethod
    def register(cls, name: str, compressor: ICompressor) -> None:
        """Register a compression implementation"""
        try:
            cls._compressors[name] = compressor
            # Set as default if first registration
            if not cls._active_compressor:
                cls._active_compressor = name
            logger.debug(f"Registered compressor: {name}")

        except Exception as e:
            logger.error(f"Compressor registration failed: {str(e)}", name=name)
            raise CompressionError(
                f"Failed to register compressor '{name}': {str(e)}"
            )

    @classmethod
    def unregister(cls, name: str) -> None:
        """Remove a registered compressor"""
        try:
            if name not in cls._compressors:
                raise CompressionError(f"Compressor '{name}' not found")

            del cls._compressors[name]

            # Clear active if it was this compressor
            if cls._active_compressor == name:
                cls._active_compressor = ""

            logger.debug(f"Unregistered compressor: {name}")

        except Exception as e:
            logger.error(f"Compressor unregistration failed: {str(e)}", name=name)
            raise

    @classmethod
    def get(cls, name: str) -> ICompressor:
        """Get a registered compressor"""
        try:
            if name not in cls._compressors:
                raise CompressionError(f"Compressor '{name}' not found")
            return cls._compressors[name]

        except Exception as e:
            logger.error(f"Compressor lookup failed: {str(e)}", name=name)
            raise

    @classmethod
    def get_active(cls) -> ICompressor:
        """Get the active compressor"""
        try:
            if not cls._active_compressor:
                raise CompressionError("No active compressor set")
            return cls._compressors[cls._active_compressor]

        except Exception as e:
            logger.error(f"Active compressor lookup failed: {str(e)}")
            raise

    @classmethod
    def set_active(cls, name: str) -> None:
        """Set the active compressor"""
        try:
            if name not in cls._compressors:
                raise CompressionError(f"Compressor '{name}' not found")

            cls._active_compressor = name
            logger.debug(f"Set active compressor: {name}")

        except Exception as e:
            logger.error(f"Setting active compressor failed: {str(e)}", name=name)
            raise

    @classmethod
    def list_compressors(cls) -> list[str]:
        """List all registered compressors"""
        return list(cls._compressors.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registrations"""
        cls._compressors.clear()
        cls._active_compressor = ""
        logger.debug("Cleared compression registry")


# Register default compressors
def register_default_compressors():
    """Register default compression implementations"""
    try:
        CompressionRegistry.register("gzip", GzipCompressor())
        CompressionRegistry.register("zip", ZipCompressor())
        CompressionRegistry.set_active("gzip")  # Set gzip as default
        logger.debug("Registered default compressors")

    except Exception as e:
        logger.error(f"Failed to register default compressors: {str(e)}")
        raise CompressionError(f"Failed to register default compressors: {str(e)}")


# Auto-register on import
register_default_compressors()
