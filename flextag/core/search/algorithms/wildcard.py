import re
from typing import Any
from flextag.core.interfaces.search import ISearchAlgorithm, ISearchQuery
from flextag.core.types.metadata import Metadata
from flextag.core.types.section import Section
from flextag.exceptions import SearchError
from flextag.logger import logger


class WildcardMatchAlgorithm(ISearchAlgorithm):
    """Search algorithm supporting wildcards"""

    def supports_wildcards(self) -> bool:
        return True

    def _wildcard_match(self, pattern: str, value: str) -> bool:
        """Enhanced wildcard matching using regex with case sensitivity"""
        try:
            # Convert pattern to regex
            regex_pattern = []
            i = 0
            while i < len(pattern):
                if pattern[i] == '*':
                    regex_pattern.append('.*')
                elif pattern[i] == '?':
                    regex_pattern.append('.')
                elif pattern[i] == '[':
                    end = pattern.find(']', i)
                    if end == -1:
                        raise SearchError("Unmatched bracket")

                    # Get the content between brackets
                    class_content = pattern[i+1:end]
                    if class_content.startswith('!') or class_content.startswith('^'):
                        # Handle negated character class
                        class_content = '^' + class_content[1:]

                    # Preserve case sensitivity for ranges
                    regex_pattern.append(f'[{class_content}]')
                    i = end
                else:
                    regex_pattern.append(re.escape(pattern[i]))
                i += 1

            final_pattern = f'^{"".join(regex_pattern)}$'
            print(f"Debug - Regex pattern: {final_pattern}")  # Debug print
            print(f"Debug - Matching value: {value}")  # Debug print

            result = bool(re.match(final_pattern, value))
            print(f"Debug - Match result: {result}")  # Debug print
            return result

        except Exception as e:
            logger.error(f"Wildcard match error: {str(e)}")
            return False

    def _matches_any_wildcard(self, pattern: str, values: list[str]) -> bool:
        """Check if pattern matches any value in list"""
        return any(self._wildcard_match(pattern, value) for value in values)

    def _compare_values(
            self,
            metadata_value: Any,
            query_value: Any,
            allow_wildcards: bool = True
    ) -> bool:
        """Compare values with optional wildcard support"""
        try:
            # Handle string comparisons with possible wildcards
            if isinstance(metadata_value, str) and isinstance(query_value, str):
                if allow_wildcards and ("*" in query_value or "?" in query_value or "[" in query_value):
                    return self._wildcard_match(query_value, str(metadata_value))
                return metadata_value == query_value

            # Handle list comparisons
            if isinstance(metadata_value, list) and isinstance(query_value, list):
                return all(
                    any(
                        self._compare_values(mv, qv, allow_wildcards)
                        for mv in metadata_value
                    )
                    for qv in query_value
                )

            # Default comparison
            return metadata_value == query_value

        except Exception as e:
            logger.error(f"Value comparison error: {str(e)}")
            return False

    def matches_metadata(self, metadata: Metadata, query: ISearchQuery) -> bool:
        """Check if metadata matches query with wildcard support"""
        try:
            # Check ID match
            if query.get_id():
                if not self._wildcard_match(query.get_id(), metadata.id):
                    return False

            # Check tag matches
            for tag_pattern in query.get_tags():
                # Check if any tag matches the pattern
                matched = any(self._wildcard_match(tag_pattern, tag) for tag in metadata.tags)
                print(f"Debug - Tag pattern '{tag_pattern}' against tags {metadata.tags}: {matched}")
                if not matched:
                    return False

            # Check path matches
            for path_pattern in query.get_paths():
                if not any(self._wildcard_match(path_pattern, path) for path in metadata.paths):
                    return False

            # Check parameter matches
            for key, value in query.get_parameters().items():
                if key not in metadata.parameters:
                    return False
                param = metadata.parameters[key]
                if not self._compare_values(param.value, value, allow_wildcards=True):
                    return False

            return True

        except Exception as e:
            logger.error(f"Wildcard metadata match error: {str(e)}")
            return False

    def matches_section(self, section: Section, query: ISearchQuery) -> bool:
        """Check if section matches query with wildcard support"""
        return self.matches_metadata(section.metadata, query)