from typing import Dict, Any

from ...logger import logger
from ..base.search import BaseSearchAlgorithm
from ..interfaces.search import ISearchQuery
from ..interfaces.section import ISection


class ExactMatchAlgorithm(BaseSearchAlgorithm):
    def supports_wildcards(self) -> bool:
        return False

    def matches_metadata(self, metadata: Dict[str, Any], query: ISearchQuery) -> bool:
        """Check if metadata matches query"""
        try:
            logger.debug(f"\nMatching metadata against query:")
            logger.debug(f"Metadata: {metadata}")
            logger.debug(f"Query: tags={query.get_tags()}, paths={query.get_paths()}")

            # Check metadata matches (similar to section matching)
            # TODO: Implement metadata matching logic
            return True

        except Exception as e:
            logger.error(f"Metadata match error: {str(e)}")
            return False

    def matches_section(self, section: ISection, query: ISearchQuery) -> bool:
        """Check if section matches query"""
        try:
            logger.debug(f"\nMatching section against query:")
            logger.debug(
                f"Section: id='{section.id}', tags={section.tags}, paths={section.paths}"
            )
            logger.debug(
                f"Query: id='{query.get_id()}', tags={query.get_tags()}, paths={query.get_paths()}"
            )

            # Check ID match
            if query.get_id():
                matches = section.id == query.get_id()
                logger.debug(
                    f"ID comparison: '{section.id}' == '{query.get_id()}' -> {matches}"
                )
                if not matches:
                    return False

            # Check tag matches
            for tag in query.get_tags():
                matches = tag in section.tags
                logger.debug(f"Tag comparison: '{tag}' in {section.tags} -> {matches}")
                if not matches:
                    return False

            # Check path matches
            for path in query.get_paths():
                matches = path in section.paths
                logger.debug(
                    f"Path comparison: '{path}' in {section.paths} -> {matches}"
                )
                if not matches:
                    return False

            logger.debug("All criteria matched successfully")
            return True

        except Exception as e:
            logger.error(f"Match error: {str(e)}")
            return False


class WildcardMatchAlgorithm(BaseSearchAlgorithm):
    """Search algorithm supporting wildcards"""

    def supports_wildcards(self) -> bool:
        return True

    def _wildcard_match(self, pattern: str, value: str) -> bool:
        """Check if value matches wildcard pattern"""
        if pattern.startswith("*") and pattern.endswith("*"):
            return pattern[1:-1] in value
        elif pattern.startswith("*"):
            return value.endswith(pattern[1:])
        elif pattern.endswith("*"):
            return value.startswith(pattern[:-1])
        return pattern == value

    def matches(self, section: ISection, query: ISearchQuery) -> bool:
        """Check matches including wildcards"""
        try:
            # Check ID match
            if query.get_id():
                if not any(self._wildcard_match(query.get_id(), section.id)):
                    return False

            # Check tag matches with wildcards
            for tag in query.get_tags():
                if not any(self._wildcard_match(tag, t) for t in section.tags):
                    return False

            # Check path matches with wildcards
            for path in query.get_paths():
                if not any(self._wildcard_match(path, p) for p in section.paths):
                    return False

            # Check parameter matches (no wildcards in parameters yet)
            for key, value in query.get_parameters().items():
                if (
                    key not in section.parameters
                    or str(section.parameters[key]) != value
                ):
                    return False

            return True

        except Exception as e:
            logger.error(f"Wildcard match error: {str(e)}")
            return False
