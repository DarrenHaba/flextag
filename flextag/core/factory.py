from typing import Type
from .interfaces.section import ISection
from .interfaces.document import IDocument
from .interfaces.parser import IFlexTagParser


class FlexTagFactory:
    def __init__(
        self,
        section_cls: Type[ISection],
        document_cls: Type[IDocument],
        parser_cls: Type[IFlexTagParser],
    ):
        self.section_cls = section_cls
        self.document_cls = document_cls
        self.parser_cls = parser_cls

    def create_parser(self) -> IFlexTagParser:
        return self.parser_cls()

    def create_document(self) -> IDocument:
        return self.document_cls()

    def create_section(
        self,
        tags: list[str] = None,
        paths: list[str] = None,
        params: dict = None,
        content: str = "",
    ) -> ISection:
        return self.section_cls(tags, paths, params, content)
