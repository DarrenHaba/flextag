from abc import ABC
from typing import Dict, List, Any, Optional
from ..interfaces.document import IDocument
from ..interfaces.section import ISection


class BaseDocument(ABC, IDocument):
    def __init__(self):
        self.settings: Dict[str, Any] = {}
        self.info: Optional[ISection] = None
        self.sections: List[ISection] = []

    def add_section(self, section: ISection):
        self.sections.append(section)

    def find(self, query: str, match_type: str = "contains") -> List[ISection]:
        return [s for s in self.sections if s.matches(query, match_type)]

    def find_one(self, query: str, match_type: str = "contains") -> Optional[ISection]:
        matches = self.find(query, match_type)
        return matches[0] if matches else None
