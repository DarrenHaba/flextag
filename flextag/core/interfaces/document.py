from typing import Protocol, Dict, List, Any, Optional

from flextag.core.interfaces.section import ISection


class IDocument(Protocol):
    settings: Dict[str, Any]
    info: Optional["ISection"]
    sections: List["ISection"]

    def add_section(self, section: "ISection"): ...
    def find(self, query: str, match_type: str = "contains") -> List["ISection"]: ...
    def find_one(
        self, query: str, match_type: str = "contains"
    ) -> Optional["ISection"]: ...
    def to_string(self) -> str: ...
    @classmethod
    def from_string(cls, content: str) -> "IDocument": ...
