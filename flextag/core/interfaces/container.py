from typing import Protocol, Dict, List, Any, Optional

from .section import ISection


class IContainer(Protocol):
    """Interface for FlexTag data containers"""

    metadata: Dict[str, Any]  # Container metadata
    params: Dict[str, Any]  # Default parameters
    sections: List[ISection]  # Container sections

    def add_section(self, section: "ISection") -> None:
        """Add a section to the container"""
        ...

    def find_first(self, query: str) -> Optional["ISection"]:
        """Find first section matching query using new query syntax"""
        ...

    def search(self, query: str) -> List["ISection"]:
        """Find all sections matching query using new query syntax"""
        ...

    def to_string(self) -> str:
        """Convert container to FlexTag format"""
        ...

    @classmethod
    def from_string(cls, content: str) -> "IContainer":
        """Create container from FlexTag format"""
        ...
