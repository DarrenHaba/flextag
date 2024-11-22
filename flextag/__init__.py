"""
FlexTag - Universal Data Container System
"""

# Core implementations
from .core.impl.section import Section
from .core.impl.container import Container
from .core.impl.parser import FlexTagParser
from .core.impl.transport import TransportContainer
from .core.impl.compressor import GzipCompressor, ZipCompressor

# Interfaces
from .core.interfaces.compressor import ICompressor

# Compression system
from .core.compression import CompressionRegistry

# Factory and utilities
from .core.factory import FlexTagFactory
from .settings import Const
from .logger import logger

# Exceptions
from .exceptions import (
    FlexTagError,
    ContainerError,
    ParameterError,
    TransportError,
    SearchError,
    EncodingError,
    CompressionError
)

# Create default factory instance
factory = FlexTagFactory(
    section_cls=Section,
    container_cls=Container,
    parser_cls=FlexTagParser,
    transport_cls=TransportContainer
)

# Register default compressors
CompressionRegistry.register('gzip', GzipCompressor)
CompressionRegistry.register('zip', ZipCompressor)

__all__ = [
    # Core classes
    "Section",
    "Container",
    "FlexTagParser",
    "TransportContainer",
    "FlexTagFactory",

    # Compression system
    "ICompressor",
    "GzipCompressor",
    "ZipCompressor",
    "CompressionRegistry",

    # Factory instance
    "factory",

    # Utilities
    "Const",
    "logger",

    # Exceptions
    "FlexTagError",
    "ContainerError",
    "ParameterError",
    "TransportError",
    "SearchError",
    "EncodingError",
    "CompressionError"
]

__version__ = "0.3.0"
