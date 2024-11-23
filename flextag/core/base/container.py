from abc import ABC
from typing import Dict, List, Any, Optional

from ..factory import SearchFactory
from ..interfaces.container import IContainer
from ..interfaces.section import ISection
from ...exceptions import SearchError
from ...logger import logger


class BaseContainer(ABC, IContainer):
    def __init__(self):
        self.metadata: Dict[str, Any] = {}
        self.params: Dict[str, Any] = {}
        self.sections: List[ISection] = []

    def add_section(self, section: ISection) -> None:
        """Add a section to the container"""
        logger.debug(f"Adding section to container: id={section.id}")
        self.sections.append(section)

    def filter(self, query: str) -> List["IContainer"]:
        """Filter containers based on metadata query"""
        try:
            logger.debug(f"Filtering container with query: {query}")
            logger.debug(f"Container metadata: {self.metadata}")

            query_obj = SearchFactory.create_query(query)
            algorithm = SearchFactory.create_algorithm(query_obj)

            # Check if this container's metadata matches
            if algorithm.matches_metadata(self.metadata, query_obj):
                logger.debug("Container matches metadata filter")
                return [self]

            logger.debug("Container does not match metadata filter")
            return []

        except Exception as e:
            logger.error(f"Filter error: {str(e)}", query=query)
            raise SearchError(f"Filter failed: {str(e)}")

    def search(self, query_str: str) -> List[ISection]:
        """Search sections using query"""
        try:
            logger.debug(f"\nStarting search with query: '{query_str}'")
            query = SearchFactory.create_query(query_str)
            algorithm = SearchFactory.create_algorithm(query)

            results = [
                s for s in self.sections if algorithm.matches_section(s, query)
            ]  # Updated to matches_section
            logger.debug(f"Found {len(results)} matching sections")
            return results

        except Exception as e:
            logger.error(f"Search error: {str(e)}", query=query_str)
            raise SearchError(f"Search failed: {str(e)}")

    def find_first(self, query_str: str) -> Optional[ISection]:
        """Find first section matching query"""
        try:
            logger.debug(f"\nStarting find_first with query: '{query_str}'")
            query = SearchFactory.create_query(query_str)
            algorithm = SearchFactory.create_algorithm(query)

            logger.debug(f"Searching through {len(self.sections)} sections")
            for section in self.sections:
                if algorithm.matches_section(
                    section, query
                ):  # Updated to matches_section
                    logger.debug(f"Found matching section: {section.id}")
                    return section

            logger.debug("No matching section found")
            return None

        except Exception as e:
            logger.error(f"Find first error: {str(e)}", query=query_str)
            raise SearchError(f"Find first failed: {str(e)}")
