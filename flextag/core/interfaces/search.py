from typing import Protocol, List, Dict, Any, Optional
from flextag.core.types.container import Container
from flextag.core.types.section import Section
from flextag.core.types.metadata import Metadata


class ISearchQuery(Protocol):
    """Interface for parsed search queries"""

    def has_wildcards(self) -> bool:
        """Check if query contains wildcards"""
        ...

    def get_tags(self) -> List[str]:
        """Get tag filters"""
        ...

    def get_paths(self) -> List[str]:
        """Get path filters"""
        ...

    def get_id(self) -> Optional[str]:
        """Get ID filter"""
        ...

    def get_parameters(self) -> Dict[str, Any]:
        """Get parameter filters"""
        ...

    def get_operators(self) -> List[str]:
        """Get logical operators (AND, OR, NOT)"""
        ...


class ISearchAlgorithm(Protocol):
    """Interface for search algorithms"""

    def supports_wildcards(self) -> bool:
        """Whether algorithm supports wildcard matching"""
        ...

    def matches_metadata(self, metadata: Metadata, query: ISearchQuery) -> bool:
        """Check if metadata matches query"""
        ...

    def matches_section(self, section: Section, query: ISearchQuery) -> bool:
        """Check if section matches query"""
        ...


class ISearchEngine(Protocol):
    """Interface for search operations"""

    def filter(self, containers: List[Container], query: str) -> List[Container]:
        """Filter containers based on metadata query"""
        ...

    def find(self, container: Container, query: str) -> List[Section]:
        """Find all matching sections"""
        ...

    def find_first(self, container: Container, query: str) -> Optional[Section]:
        """Find first matching section"""
        ...
