from abc import ABC
from typing import Any, Dict, Type
from ..interfaces.parser import IContentParser, IFlexTagParser


class BaseContentParser(ABC, IContentParser):
    def parse(self, content: str) -> Any:
        raise NotImplementedError

    def dump(self, data: Any) -> str:
        raise NotImplementedError


class BaseFlexTagParser(ABC, IFlexTagParser):
    def __init__(self):
        self.content_parsers: Dict[str, Type[IContentParser]] = {}

    def register_content_parser(self, fmt: str, parser: Type[IContentParser]):
        self.content_parsers[fmt] = parser

    def get_content_parser(self, fmt: str) -> IContentParser:
        if fmt not in self.content_parsers:
            raise ValueError(f"No parser registered for format: {fmt}")
        return self.content_parsers[fmt]()
