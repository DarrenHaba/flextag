from typing import Type

from typing import Type

from .base.search import BaseSearchQuery
from .impl.search import WildcardMatchAlgorithm, ExactMatchAlgorithm
from .interfaces.compressor import ICompressor
from .interfaces.search import ISearchQuery, ISearchAlgorithm
from .interfaces.section import ISection
from .interfaces.container import IContainer
from .interfaces.parser import IFlexTagParser
from .interfaces.transport import ITransportContainer


class FlexTagFactory:
    """Factory for creating FlexTag components"""

    def __init__(
        self,
        section_cls: Type[ISection],
        container_cls: Type[IContainer],
        parser_cls: Type[IFlexTagParser],
        transport_cls: Type[ITransportContainer] = None,
    ):
        self.section_cls = section_cls
        self.container_cls = container_cls
        self.parser_cls = parser_cls
        self.transport_cls = transport_cls

    def register_compression(self, name: str, handler: Type[ICompressor]) -> None:
        """Register compression handler"""
        from .compression.registry import CompressionRegistry

        CompressionRegistry.register(name, handler)

    def create_parser(self) -> IFlexTagParser:
        return self.parser_cls()

    def create_container(self) -> IContainer:
        return self.container_cls()

    def create_section(
        self,
        id: str = "",
        tags: list[str] = None,
        paths: list[str] = None,
        parameters: dict = None,
        content: str = "",
        **kwargs
    ) -> ISection:
        return self.section_cls(
            id=id,
            tags=tags or [],
            paths=paths or [],
            parameters=parameters or {},
            content=content,
            **kwargs
        )

    def create_transport(self) -> ITransportContainer:
        if not self.transport_cls:
            raise ValueError("No transport class registered")
        return self.transport_cls()


class SearchFactory:
    """Factory for search components"""

    @staticmethod
    def create_query(query_str: str) -> ISearchQuery:
        return BaseSearchQuery(query_str)

    @staticmethod
    def create_algorithm(query: ISearchQuery) -> ISearchAlgorithm:
        if query.has_wildcards():
            return WildcardMatchAlgorithm()
        return ExactMatchAlgorithm()
