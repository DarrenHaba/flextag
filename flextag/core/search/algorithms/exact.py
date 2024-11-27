from flextag.core.interfaces.search import ISearchAlgorithm, ISearchQuery
from flextag.core.types.metadata import Metadata
from flextag.core.types.section import Section
from flextag.logger import logger


class ExactMatchAlgorithm(ISearchAlgorithm):
    """Simple exact match search algorithm"""

    def supports_wildcards(self) -> bool:
        return False

    def matches_metadata(self, metadata: Metadata, query: ISearchQuery) -> bool:
        """Check if metadata matches query with exact matching"""
        try:
            logger.debug(
                f"\nMatching metadata against query: "
                f"id={query.get_id()}, "
                f"tags={query.get_tags()}, "
                f"paths={query.get_paths()}"
            )

            # Check ID match
            if query.get_id() and metadata.id != query.get_id():
                return False

            # Check tag matches
            for tag in query.get_tags():
                if tag not in metadata.tags:
                    return False

            # Check path matches
            for path in query.get_paths():
                if path not in metadata.paths:
                    return False

            # Check parameter matches
            for key, value in query.get_parameters().items():
                if key not in metadata.parameters:
                    return False
                param = metadata.parameters[key]
                if param.value != value:
                    return False

            return True

        except Exception as e:
            logger.error(f"Metadata match error: {str(e)}")
            return False

    def matches_section(self, section: Section, query: ISearchQuery) -> bool:
        """Check if section matches query with exact matching"""
        return self.matches_metadata(section.metadata, query)
