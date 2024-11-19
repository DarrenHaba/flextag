from abc import ABC
from typing import List, Dict, Any
from ..interfaces.section import ISection


class BaseSection(ABC, ISection):
    def __init__(
        self,
        tags: List[str] = None,
        paths: List[str] = None,
        params: Dict[str, Any] = None,
        content: str = "",
    ):
        self.tags = tags or []
        self.paths = paths or []
        self.params = params or {}
        self.content = content

    def matches(self, query: str, match_type: str = "contains") -> bool:
        parts = query.strip().split()
        for part in parts:
            if part.startswith("#"):
                tag = part[1:]
                if match_type == "exact":
                    if tag not in self.tags:
                        return False
                else:
                    if not any(t.startswith(tag) for t in self.tags):
                        return False
            elif part.startswith("."):
                path = part[1:]
                if match_type == "exact":
                    if path not in self.paths:
                        return False
                else:
                    if not any(p.startswith(path) for p in self.paths):
                        return False
        return True
