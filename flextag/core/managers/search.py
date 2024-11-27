from typing import Dict, List, Optional, Type
from flextag.core.interfaces.managers import ISearchManager
from flextag.core.interfaces.search import ISearchAlgorithm, ISearchQuery
from flextag.core.types.container import Container
from flextag.core.types.section import Section
from flextag.logger import logger
from flextag.exceptions import SearchError


class SearchManager(ISearchManager):
    """Manager for search operations"""

    def __init__(self):
        self._algorithms: Dict[str, Type[ISearchAlgorithm]] = {}
        self._active_algorithm: Optional[ISearchAlgorithm] = None
        self._query_parser: Optional[Type[ISearchQuery]] = None
        logger.debug("Initialized SearchManager")

    def register_algorithm(self, name: str, algorithm: Type[ISearchAlgorithm]) -> None:
        """Register search algorithm implementation"""
        try:
            self._algorithms[name] = algorithm
            logger.debug(f"Registered search algorithm: {name}")

            # Set as active if first registered
            if not self._active_algorithm:
                self.set_active_algorithm(name)

        except Exception as e:
            logger.error(f"Failed to register algorithm: {str(e)}", name=name)
            raise SearchError(f"Failed to register algorithm '{name}': {str(e)}")

    def register_query_parser(self, parser: Type[ISearchQuery]) -> None:
        """Register query parser implementation"""
        self._query_parser = parser
        logger.debug("Registered query parser")

    def set_active_algorithm(self, name: str) -> None:
        """Set active search algorithm"""
        try:
            if name not in self._algorithms:
                raise SearchError(f"Algorithm '{name}' not found")

            self._active_algorithm = self._algorithms[name]()
            logger.debug(f"Set active algorithm to: {name}")

        except Exception as e:
            logger.error(f"Failed to set active algorithm: {str(e)}", name=name)
            raise SearchError(f"Failed to set active algorithm: {str(e)}")

    def auto_select_algorithm(self, query: str) -> None:
        """Auto-select appropriate algorithm based on query complexity"""
        try:
            if not self._query_parser:
                raise SearchError("No query parser registered")

            # Parse query to analyze complexity
            parsed_query = self._query_parser(query)

            # Select based on features needed
            if parsed_query.has_wildcards():
                # Find algorithm supporting wildcards
                for name, algo in self._algorithms.items():
                    if algo().supports_wildcards():
                        self.set_active_algorithm(name)
                        logger.debug(
                            f"Auto-selected wildcard algorithm: {name}"
                        )
                        return

                raise SearchError("No wildcard-supporting algorithm available")
            else:
                # Use simple algorithm for basic queries
                for name, algo in self._algorithms.items():
                    if not algo().supports_wildcards():
                        self.set_active_algorithm(name)
                        logger.debug(
                            f"Auto-selected basic algorithm: {name}"
                        )
                        return

            # Fallback to first registered
            name = next(iter(self._algorithms))
            self.set_active_algorithm(name)
            logger.debug(f"Fallback to algorithm: {name}")

        except Exception as e:
            logger.error(f"Failed to auto-select algorithm: {str(e)}")
            raise SearchError(f"Failed to auto-select algorithm: {str(e)}")

    def filter(self, containers: List[Container], query: str) -> List[Container]:
        """Filter containers based on metadata query"""
        try:
            if not self._active_algorithm:
                raise SearchError("No active search algorithm")
            if not self._query_parser:
                raise SearchError("No query parser registered")

            parsed_query = self._query_parser(query)

            filtered = []
            for container in containers:
                if self._active_algorithm.matches_metadata(
                        container.metadata,
                        parsed_query
                ):
                    filtered.append(container)

            logger.debug(
                f"Filtered {len(filtered)} containers from {len(containers)}"
            )
            return filtered

        except Exception as e:
            logger.error(f"Filter operation failed: {str(e)}")
            raise SearchError(f"Filter operation failed: {str(e)}")

    def find(self, container: Container, query: str) -> List[Section]:
        """Find all matching sections"""
        try:
            if not self._active_algorithm:
                raise SearchError("No active search algorithm")
            if not self._query_parser:
                raise SearchError("No query parser registered")

            parsed_query = self._query_parser(query)

            matches = []
            for section in container.sections:
                if self._active_algorithm.matches_section(
                        section,
                        parsed_query
                ):
                    matches.append(section)

            logger.debug(
                f"Found {len(matches)} matching sections"
            )
            return matches

        except Exception as e:
            logger.error(f"Find operation failed: {str(e)}")
            raise SearchError(f"Find operation failed: {str(e)}")

    def find_first(self, container: Container, query: str) -> Optional[Section]:
        """Find first matching section"""
        try:
            if not self._active_algorithm:
                raise SearchError("No active search algorithm")
            if not self._query_parser:
                raise SearchError("No query parser registered")

            parsed_query = self._query_parser(query)

            for section in container.sections:
                if self._active_algorithm.matches_section(
                        section,
                        parsed_query
                ):
                    logger.debug(f"Found matching section: {section.metadata.id}")
                    return section

            logger.debug("No matching section found")
            return None

        except Exception as e:
            logger.error(f"Find first operation failed: {str(e)}")
            raise SearchError(f"Find first operation failed: {str(e)}")
