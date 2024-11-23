"""
FlexTag - Universal Data Container System
"""

from typing import List

from .core.containers import ContainerManager

# Core implementations
from .core.impl.section import Section
from .core.impl.container import Container
from .core.impl.parser import FlexTagParser
from .core.impl.transport import TransportContainer
from .core.impl.compressor import GzipCompressor, ZipCompressor
from .core.factory import FlexTagFactory

# Interfaces
from .core.interfaces.compressor import ICompressor

# Compression system
from .core.compression import CompressionRegistry

# Factory and utilities
from .core.factory import FlexTagFactory
from .core.interfaces.container import IContainer
from .core.interfaces.section import ISection
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
    CompressionError,
)

# Create default factory instance
_factory = FlexTagFactory(
    section_cls=Section, container_cls=Container, parser_cls=FlexTagParser
)


def parse(content: str) -> IContainer:
    """Parse FlexTag content into a container"""
    parser = _factory.create_parser()
    return parser.parse(content)


def create_section(**kwargs) -> ISection:
    """Create a new section"""
    return _factory.create_section(**kwargs)


def create_container() -> IContainer:
    """Create a new container"""
    return _factory.create_container()


def load_containers(paths: List[str]) -> ContainerManager:
    """Load multiple containers from files"""
    containers = []
    for path in paths:
        with open(path) as f:
            containers.append(parse(f.read()))
    return ContainerManager(containers)


# Register default compressors
CompressionRegistry.register("gzip", GzipCompressor)
CompressionRegistry.register("zip", ZipCompressor)

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
    # "factory",
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
    "CompressionError",
]

__version__ = "0.3.0"
