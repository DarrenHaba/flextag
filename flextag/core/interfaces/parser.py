from typing import Protocol, Dict, Type, Any
from .container import IContainer


class IContentParser(Protocol):
    """Parser for section content based on format"""

    def parse(self, content: str) -> Any:
        """Parse content string to native format"""
        ...

    def dump(self, data: Any) -> str:
        """Convert native format to string"""
        ...


class IFlexTagParser(Protocol):
    """Parser for FlexTag container structure"""

    content_parsers: Dict[str, Type[IContentParser]]

    def parse(self, content: str) -> IContainer:
        """Parse string to container"""
        ...

    def dump(self, container: IContainer) -> str:
        """Convert container to string"""
        ...

    def register_content_parser(self, fmt: str, parser: Type[IContentParser]) -> None:
        """Register content parser for format"""
        ...
