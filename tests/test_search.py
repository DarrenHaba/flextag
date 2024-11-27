from decimal import Decimal

import pytest

from flextag.core.search.algorithms.exact import ExactMatchAlgorithm
from flextag.core.search.algorithms.wildcard import WildcardMatchAlgorithm
from flextag.core.search.query import SearchQuery
from flextag.core.types.metadata import Metadata
from flextag.exceptions import SearchError, ParameterError
from flextag.core.types.parameter import ParameterValue, ParameterType
from flextag.core.types.section import Section


# Fixtures
@pytest.fixture
def metadata():
    """Create test metadata with various types."""
    metadata = Metadata(
        id="config",
        tags=["system", "database", "sysXconfig", "prod"],
        paths=["sys.config", "db.settings"],
        fmt="json"
    )
    metadata.add_parameter("port", "8080")
    metadata.add_parameter("active", "true")
    metadata.add_parameter("env", "production")
    metadata.add_parameter("version", "2.1")
    metadata.add_parameter("tags", '["config", "system"]')
    return metadata


@pytest.fixture
def section(metadata):
    """Create test section."""
    return Section(
        metadata=metadata,
        content='{"port": 8080}',
        raw_content='{"port": 8080}'
    )


@pytest.fixture
def exact_algorithm():
    """Create exact match algorithm."""
    return ExactMatchAlgorithm()


@pytest.fixture
def wildcard_algorithm():
    """Create wildcard match algorithm."""
    return WildcardMatchAlgorithm()


# Test Classes
class TestTypedSearchQuery:
    """Test typed search query functionality."""

    def test_numeric_comparison_operators(self, metadata):
        """Test all numeric comparison operators."""
        # Greater than or equal
        query = SearchQuery("port>=8080")
        assert query.evaluate(metadata) == True

        # Less than or equal
        query = SearchQuery("port<=8080")
        assert query.evaluate(metadata) == True

        # Not equal (if supported)
        query = SearchQuery("port!=9000")
        assert query.evaluate(metadata) == True


    def test_array_operations(self, metadata):
        """Test array operations."""
        # IN operator
        query = SearchQuery('tags IN ["config"]')
        assert query.evaluate(metadata) == True

        # NOT IN operator
        query = SearchQuery('tags NOT IN ["deprecated"]')
        assert query.evaluate(metadata) == True

    def test_type_safety(self, metadata):
        """Test type safety enforcement."""
        # String with numeric operation
        with pytest.raises(SearchError):
            query = SearchQuery("env>2000")
            query.evaluate(metadata)

        # Numeric with boolean
        with pytest.raises(SearchError):
            query = SearchQuery("port=true")
            query.evaluate(metadata)

        # Array with non-array
        with pytest.raises(SearchError):
            query = SearchQuery("tags=42")
            query.evaluate(metadata)

    def test_nested_boolean_operations(self, metadata):
        """Test nested boolean operations."""
        query = SearchQuery("(port>8000 AND active=true) OR env='production'")
        assert query.evaluate(metadata) == True

        query = SearchQuery("NOT (port<8000 OR active=false)")
        assert query.evaluate(metadata) == True

    def test_numeric_comparisons(self, metadata):
        """Test numeric parameter comparisons."""
        query = SearchQuery('port=8080')
        assert query.evaluate(metadata) == True

        query = SearchQuery('port>8000')
        assert query.evaluate(metadata) == True

        query = SearchQuery('port<9000')
        assert query.evaluate(metadata) == True

    def test_float_comparisons(self, metadata):
        """Test float parameter comparisons."""
        query = SearchQuery("version>2.0")
        assert query.evaluate(metadata) == True

    def test_boolean_parameters(self, metadata):
        """Test boolean parameter matching."""
        query = SearchQuery("active=true")
        assert query.evaluate(metadata) == True

    def test_complex_typed_queries(self, metadata):
        """Test complex queries with typed parameters."""
        query = SearchQuery("port>8000 AND active=true")
        assert query.evaluate(metadata) == True


class TestParameterValue:
    """Test parameter value handling."""

    def test_decimal_handling(self):
        """Test decimal number handling."""
        # Parse decimal
        param = ParameterValue.parse("123.456m")
        assert param.type == ParameterType.DECIMAL
        assert isinstance(param.value, Decimal)
        assert str(param.value) == "123.456"

        # Parse float
        param = ParameterValue.parse("123.456f")
        assert param.type == ParameterType.FLOAT
        assert isinstance(param.value, float)

        # Parse double
        param = ParameterValue.parse("123.456d")
        assert param.type == ParameterType.DOUBLE
        assert isinstance(param.value, float)

    def test_numeric_precision(self):
        """Test numeric precision handling."""
        decimal_str = "0.1234567890123456789"
        param = ParameterValue.parse(f"{decimal_str}m")
        assert str(param.value) == decimal_str  # Decimal maintains precision

        param = ParameterValue.parse(f"{decimal_str}d")
        assert len(str(param.value)) < len(decimal_str)  # Double has less precision

    def test_array_type_handling(self):
        """Test array type handling."""
        # Mixed type array
        param = ParameterValue.parse('[1, "two", true, 3.14]')
        assert param.type == ParameterType.ARRAY
        assert len(param.value) == 4
        assert isinstance(param.value[0], int)
        assert isinstance(param.value[1], str)
        assert isinstance(param.value[2], bool)
        assert isinstance(param.value[3], float)

        # Nested array
        param = ParameterValue.parse('[[1,2], ["a","b"]]')
        assert param.type == ParameterType.ARRAY
        assert isinstance(param.value[0], list)

    def test_string_parsing(self):
        """Test string parameter parsing."""
        param = ParameterValue.parse("test")
        assert param.type == ParameterType.STRING
        assert param.value == "test"

    def test_numeric_parsing(self):
        """Test numeric parameter parsing."""
        param = ParameterValue.parse("42")
        assert param.type == ParameterType.INTEGER

    def test_boolean_parsing(self):
        """Test boolean parameter parsing."""
        param = ParameterValue.parse("true")
        assert param.type == ParameterType.BOOLEAN

    def test_array_parsing(self):
        """Test array parameter parsing."""
        param = ParameterValue.parse('["one", "two"]')
        assert param.type == ParameterType.ARRAY
        assert param.value == ["one", "two"]

    def test_invalid_values(self):
        """Test handling of invalid values."""
        with pytest.raises(ParameterError):
            ParameterValue.parse("[invalid")


class TestExactMatchAlgorithm:
    """Test exact match search algorithm."""

    def test_id_match(self, exact_algorithm, metadata):
        """Test exact ID matching."""
        query = SearchQuery(":config")
        assert exact_algorithm.matches_metadata(metadata, query)

    def test_combined_match(self, exact_algorithm, metadata):
        """Test combining multiple criteria."""
        query = SearchQuery(":config #system .sys.config")
        assert exact_algorithm.matches_metadata(metadata, query)


class TestWildcardMatchAlgorithm:
    """Test wildcard match search algorithm."""

    def test_single_character_wildcard(self, wildcard_algorithm, metadata):
        """Test single character wildcard."""
        pattern = "sys?config"
        query = SearchQuery(f"#{pattern}")
        actual = wildcard_algorithm.matches_metadata(metadata, query)
        expected = True
        print(f"Pattern: {pattern}, Metadata: {metadata.tags}, Expected: {expected}, Actual: {actual}")
        assert actual == expected

    def test_character_class(self, wildcard_algorithm, metadata):
        """Test character class wildcard."""
        pattern = "sys[tw]*"
        query = SearchQuery(f"#{pattern}")
        actual = wildcard_algorithm.matches_metadata(metadata, query)
        expected = True
        print(f"Pattern: {pattern}, Metadata: {metadata.tags}, Expected: {expected}, Actual: {actual}")
        assert actual == expected

    def test_negated_character_class(self, wildcard_algorithm, metadata):
        """Test negated character class wildcard."""
        # Add a tag that should actually match the pattern
        metadata.tags.append("prodX")  # Adding a tag that should match

        pattern = "prod[!0-9]"  # Matches "prod" + exactly one non-digit character
        query = SearchQuery(f"#{pattern}")
        actual = wildcard_algorithm.matches_metadata(metadata, query)
        print(f"Pattern: {pattern}")
        print(f"Tags: {metadata.tags}")
        print(f"Actual: {actual}")
        print(f"Expected: True")
        print(f"Debug - Testing pattern '{pattern}' against each tag:")
        for tag in metadata.tags:
            match = wildcard_algorithm._wildcard_match(pattern, tag)
            print(f"  - Tag '{tag}': {match}")
        assert actual == True

    def test_character_class_examples(self, wildcard_algorithm):
        """Test various character class patterns"""
        test_cases = [
            ("prod[!0-9]", "prodA", True),    # Matches: one non-digit
            ("prod[!0-9]", "prod5", False),   # Doesn't match: digit
            ("prod[!0-9]", "prod", False),    # Doesn't match: missing character
            ("prod[!0-9]", "prodAB", False),  # Doesn't match: too many characters
            ("prod[a-z]", "proda", True),     # Matches: lowercase letter
            ("prod[a-z]", "prodA", False),    # Doesn't match: uppercase letter
        ]

        for pattern, test_value, expected in test_cases:
            result = wildcard_algorithm._wildcard_match(pattern, test_value)
            print(f"Pattern: {pattern}, Value: {test_value}, Expected: {expected}, Got: {result}")
            assert result == expected, f"Failed matching '{test_value}' against '{pattern}'"

    def test_character_range(self, wildcard_algorithm, metadata):
        """Test character range wildcard."""
        pattern = "[a-z]ystem"
        query = SearchQuery(f"#{pattern}")
        actual = wildcard_algorithm.matches_metadata(metadata, query)
        expected = True
        print(f"Pattern: {pattern}, Metadata: {metadata.tags}, Expected: {expected}, Actual: {actual}")
        assert actual == expected

    def test_no_match(self, wildcard_algorithm, metadata):
        """Test no match wildcard."""
        pattern = "wrong[0-9]"
        query = SearchQuery(f"#{pattern}")
        actual = wildcard_algorithm.matches_metadata(metadata, query)
        expected = False
        print(f"Pattern: {pattern}, Metadata: {metadata.tags}, Expected: {expected}, Actual: {actual}")
        assert actual == expected

    def test_id_wildcard(self, wildcard_algorithm, metadata):
        """Test ID wildcard matching."""
        query = SearchQuery(":conf*")
        assert wildcard_algorithm.matches_metadata(metadata, query)

    def test_path_wildcard(self, wildcard_algorithm, metadata):
        """Test path wildcard matching."""
        query = SearchQuery(".sys.*")
        assert wildcard_algorithm.matches_metadata(metadata, query)


@pytest.mark.parametrize("algorithm", [
    pytest.param(ExactMatchAlgorithm(), id="exact"),
    pytest.param(WildcardMatchAlgorithm(), id="wildcard")
])
class TestCommonBehavior:
    """Test behavior common to all algorithms."""

    def test_empty_query(self, algorithm, metadata):
        """Test matching empty query."""
        query = SearchQuery("")
        assert algorithm.matches_metadata(metadata, query)

    def test_multiple_criteria(self, algorithm, metadata):
        """Test matching multiple criteria."""
        query = SearchQuery(":config #system #database")
        assert algorithm.matches_metadata(metadata, query)
