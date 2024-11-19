from .core.impl.section import Section
from .core.impl.document import Document
from .core.impl.parser import FlexTagParser
from .core.factory import FlexTagFactory
from .settings import Const
from .logger import logger

# Create default factory instance
factory = FlexTagFactory(
    section_cls=Section, document_cls=Document, parser_cls=FlexTagParser
)

# Export commonly used classes and instances
__all__ = [
    "Section",
    "Document",
    "FlexTagParser",
    "FlexTagFactory",
    "factory",
    "Const",
    "logger",
]

__version__ = "0.3.0"
