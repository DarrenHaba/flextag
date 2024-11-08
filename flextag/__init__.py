"""
FlexTag - A flexible tag-based markup format parser and serializer.
"""

from .parser import parse
from .serializer import dumps
from .json import to_json, from_json
from .exceptions import (
    FlexTagError,
    ParseError,
    SerializationError,
    ValidationError,
    WrapperError,
    TagError,
    StructureError,
)

__version__ = "0.3.0"
__all__ = [
    # Main functions
    "parse",
    "dumps",
    "to_json",
    "from_json",
    # Exceptions
    "FlexTagError",
    "ParseError",
    "SerializationError",
    "ValidationError",
    "WrapperError",
    "TagError",
    "StructureError",
]
