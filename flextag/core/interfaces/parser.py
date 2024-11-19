from typing import Any, Dict, Type, Protocol


class IContentParser(Protocol):
    """Handles parsing of section content based on format"""

    def parse(self, content: str) -> Any: ...
    def dump(self, data: Any) -> str: ...


class IFlexTagParser(Protocol):
    """Handles parsing of FlexTag document structure"""

    content_parsers: Dict[str, Type[IContentParser]]

    def parse(self, content: str) -> "IDocument": ...
    def dump(self, document: "IDocument") -> str: ...
    def register_content_parser(self, fmt: str, parser: Type[IContentParser]): ...
