from typing import Protocol, Dict, List, Any


class ISection(Protocol):
    tags: List[str]
    paths: List[str]
    params: Dict[str, Any]
    content: str

    def matches(self, query: str, match_type: str = "contains") -> bool: ...
    @classmethod
    def from_header(cls, header: str, content: str = "") -> "ISection": ...
