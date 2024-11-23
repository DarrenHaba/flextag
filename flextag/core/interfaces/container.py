from typing import Protocol, Dict, List, Any, Optional
from .section import ISection


class IContainer(Protocol):
    """Interface for FlexTag containers"""

    metadata: Dict[str, Any]
    params: Dict[str, Any]
    sections: List[ISection]

    def filter(self, query: str) -> List["IContainer"]:
        """Filter containers based on metadata"""
        ...

    def search(self, query: str) -> List[ISection]:
        """Search for sections across all containers"""
        ...

    def find_first(self, query: str) -> Optional[ISection]:
        """Find first matching section"""
        ...
