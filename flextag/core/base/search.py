from abc import ABC
from typing import List, Optional
from ..interfaces.search import ISearchQuery, ISearchAlgorithm
from ..interfaces.section import ISection
from ...exceptions import SearchError
from ...logger import logger


class BaseSearchQuery(ABC, ISearchQuery):
    """Base implementation of search query"""

    def __init__(self, query_str: str):
        self.query_str = query_str
        self.tags: List[str] = []
        self.paths: List[str] = []
        self.section_id: Optional[str] = None
        self.parameters: dict = {}
        self.operators: List[str] = []
        self._parse_query()

    def _parse_query(self):
        try:
            parts = self.query_str.strip().split()
            logger.debug(f"Parsing query parts: {parts}")

            for part in parts:
                if part.startswith(":"):
                    self.section_id = part[1:]
                    logger.debug(f"Found query ID: {self.section_id}")
                elif part.startswith("#"):
                    self.tags.append(part[1:])
                    logger.debug(f"Found query tag: {part[1:]}")
                elif part.startswith("."):
                    self.paths.append(part[1:])
                    logger.debug(f"Found query path: {part[1:]}")
                elif "=" in part:
                    key, value = part.split("=", 1)
                    self.parameters[key.strip()] = value.strip().strip("\"'")
                    logger.debug(
                        f"Found query parameter: {key.strip()}={self.parameters[key.strip()]}"
                    )

            logger.debug(
                f"Parsed query: id={self.section_id}, tags={self.tags}, paths={self.paths}"
            )
        except Exception as e:
            logger.error(f"Query parsing error: {str(e)}", query=self.query_str)
            raise SearchError(f"Failed to parse query: {str(e)}")

    # def _parse_query(self):
    #     """Parse query string into components"""
    #     try:
    #         parts = self.query_str.strip().split()
    #         for part in parts:
    #             if part.startswith("#"):
    #                 self.tags.append(part[1:])
    #             elif part.startswith("."):
    #                 self.paths.append(part[1:])
    #             elif part.startswith(":"):
    #                 self.section_id = part[1:]
    #             elif part in ["AND", "OR", "NOT"]:
    #                 self.operators.append(part)
    #             elif "=" in part:
    #                 key, value = part.split("=", 1)
    #                 self.parameters[key.strip()] = value.strip().strip('"\'')
    #     except Exception as e:
    #         logger.error(f"Query parsing error: {str(e)}", query=self.query_str)
    #         raise SearchError(f"Failed to parse query: {str(e)}")

    def has_wildcards(self) -> bool:
        """Check if query contains wildcards"""
        return any(
            "*" in item
            for item in self.tags
            + self.paths
            + ([self.section_id] if self.section_id else [])
        )

    def get_tags(self) -> List[str]:
        return self.tags

    def get_paths(self) -> List[str]:
        return self.paths

    def get_id(self) -> Optional[str]:
        return self.section_id

    def get_parameters(self) -> dict:
        return self.parameters

    def get_operators(self) -> List[str]:
        return self.operators


class BaseSearchAlgorithm(ABC, ISearchAlgorithm):
    """Base implementation of search algorithm"""

    def supports_wildcards(self) -> bool:
        return False

    def search(self, sections: List[ISection], query: ISearchQuery) -> List[ISection]:
        """Search sections using query"""
        try:
            if query.has_wildcards() and not self.supports_wildcards():
                raise SearchError("This algorithm doesn't support wildcard searches")

            return [s for s in sections if self.matches(s, query)]

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            raise SearchError(f"Search failed: {str(e)}")

    def matches(self, section: ISection, query: ISearchQuery) -> bool:
        """Check exact matches only"""
        try:
            logger.debug(f"ExactMatch checking section {section.id}")
            logger.debug(
                f"Query parts: id={query.get_id()}, tags={query.get_tags()}, paths={query.get_paths()}"
            )
            logger.debug(f"Section data: tags={section.tags}, paths={section.paths}")

            # Check ID match
            if query.get_id():
                matches = section.id == query.get_id()
                logger.debug(f"ID match: {matches}")
                if not matches:
                    return False

            # Check tag matches
            for tag in query.get_tags():
                matches = tag in section.tags
                logger.debug(f"Tag '{tag}' match: {matches}")
                if not matches:
                    return False

            # Check path matches
            for path in query.get_paths():
                matches = path in section.paths
                logger.debug(f"Path '{path}' match: {matches}")
                if not matches:
                    return False

            return True

        except Exception as e:
            logger.error(f"Match error: {str(e)}")
            return False
