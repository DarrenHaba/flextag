from typing import Protocol, Dict, List, Any


class ISection(Protocol):
    """Interface for FlexTag sections"""

    id: str
    tags: List[str]
    paths: List[str]
    parameters: Dict[str, Any]
    content: str

    # Add search methods
    def matches(self, query: str) -> bool: ...
