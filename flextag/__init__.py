"""Main package initialization"""
from .managers.data import DataManager
from .managers.query import QueryManager
from .core.parser.provider import ParserProvider
from .core.query.provider import QueryProvider

__version__ = "0.3.0a1"

__all__ = [
    "DataManager",
    "QueryManager",
    "ParserProvider",
    "QueryProvider"
]
