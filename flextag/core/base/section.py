from abc import ABC
from typing import List, Dict, Any
from dataclasses import dataclass, field

from ..factory import SearchFactory
from ..interfaces.section import ISection
from ...exceptions import SearchError
from ...logger import logger


@dataclass
class BaseSection(ABC, ISection):
    id: str = ""
    tags: List[str] = field(default_factory=list)
    paths: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    content: str = ""

    def matches(self, query_str: str) -> bool:
        """Check if section matches query"""
        try:
            logger.debug(f"Checking section match: id={self.id}, query={query_str}")
            query = SearchFactory.create_query(query_str)
            algorithm = SearchFactory.create_algorithm(query)
            result = algorithm.matches(self, query)
            logger.debug(f"Match result: {result}")
            return result
        except Exception as e:
            logger.error(f"Section match error: {str(e)}", query=query_str)
            raise SearchError(f"Match check failed: {str(e)}")
