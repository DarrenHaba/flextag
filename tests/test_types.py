import pytest
from decimal import Decimal
from flextag.core.types.parameter import ParameterType, ParameterValue
from flextag.core.types.metadata import MetadataParameters, Metadata
from flextag.core.types.section import Section
from flextag.core.types.container import Container
from flextag.exceptions import FlexTagError

# Add more test cases?
# Add edge case testing?
# Add performance tests?

class TestParameterValue:
    """Test parameter value parsing and typing"""

    @pytest.mark.parametrize("raw_value,expected_type,expected_value", [
        # String tests
        ('"test"', ParameterType.STRING, "test"),
        ("'test'", ParameterType.STRING, "test"),
        ('"test with spaces"', ParameterType.STRING, "test with spaces"),

        # Number tests
        ("42", ParameterType.INTEGER, 42),
        ("-42", ParameterType.INTEGER, -42),
        ("3.14", ParameterType.FLOAT, 3.14),
        ("1.0f", ParameterType.FLOAT, 1.0),
        ("1.0d", ParameterType.DOUBLE, 1.0),
        ("1.0m", ParameterType.DECIMAL, Decimal("1.0")),

        # Boolean tests
        ("true", ParameterType.BOOLEAN, True),
        ("false", ParameterType.BOOLEAN, False),
        ("TRUE", ParameterType.BOOLEAN, True),
        ("FALSE", ParameterType.BOOLEAN, False),

        # Array tests
        ('["one","two"]', ParameterType.ARRAY, ["one", "two"]),
        ("[1,2,3]", ParameterType.ARRAY, ["1", "2", "3"]),
        ('["mixed",42,true]', ParameterType.ARRAY, ["mixed", "42", "true"])
    ])
    def test_parameter_parsing(self, raw_value, expected_type, expected_value):
        """Test parsing different parameter types"""
        param = ParameterValue.parse(raw_value)
        assert param.type == expected_type
        assert param.value == expected_value

    def test_invalid_parameters(self):
        """Test handling invalid parameter values"""
        invalid_values = [
            '"unclosed string',    # Unclosed quote
            "[unclosed array",     # Unclosed array
            "invalid=value",       # Invalid format
        ]
        for value in invalid_values:
            with pytest.raises(FlexTagError):
                ParameterValue.parse(value)

    def test_parameter_comparison(self):
        """Test parameter value comparisons"""
        param1 = ParameterValue.parse('"test"')
        param2 = ParameterValue.parse('"test"')
        param3 = ParameterValue.parse('"different"')

        assert param1 == param2
        assert param1 != param3
        assert param1 == "test"  # Compare with raw value

    def test_parameter_string_conversion(self):
        """Test converting parameters back to strings"""
        test_cases = [
            ('"test"', 'test'),                    # String
            ('42', '42'),                          # Integer
            ('3.14f', '3.14'),                     # Float
            ('true', 'true'),                      # Boolean
            ('["one","two"]', '["one", "two"]'),   # Array
        ]
        for input_value, expected_str in test_cases:
            param = ParameterValue.parse(input_value)
            assert str(param.value) in param.to_string()


class TestMetadata:
    """Test metadata handling"""

    @pytest.fixture
    def basic_metadata(self):
        """Create basic metadata for testing"""
        return Metadata(
            id="test",
            tags=["tag1", "tag2"],
            paths=["path1", "path2"],
            fmt="json",
            enc="utf-8"
        )

    def test_metadata_defaults(self):
        """Test default metadata values"""
        metadata = Metadata()
        assert metadata.fmt == "text"
        assert metadata.enc == "utf-8"
        assert metadata.crypt == ""
        assert metadata.comp == ""
        assert metadata.lang == "en"

    def test_metadata_parameters(self, basic_metadata):
        """Test metadata parameter handling"""
        basic_metadata.add_parameter("string", '"value"')
        basic_metadata.add_parameter("number", "42")
        basic_metadata.add_parameter("bool", "true")

        assert basic_metadata.get_parameter("string") == "value"
        assert basic_metadata.get_parameter("number") == 42
        assert basic_metadata.get_parameter("bool") is True

    def test_metadata_serialization(self, basic_metadata):
        """Test metadata serialization"""
        data = basic_metadata.to_dict()
        restored = Metadata.from_dict(data)

        assert restored.id == basic_metadata.id
        assert restored.tags == basic_metadata.tags
        assert restored.paths == basic_metadata.paths
        assert restored.fmt == basic_metadata.fmt
        assert restored.parameters == basic_metadata.parameters


class TestSection:
    """Test section functionality"""

    @pytest.fixture
    def basic_section(self):
        """Create basic section for testing"""
        metadata = Metadata(
            id="test",
            tags=["tag1"],
            paths=["path1"],
            fmt="json"
        )
        return Section(
            metadata=metadata,
            content='{"key": "value"}',
            raw_content='{"key": "value"}'
        )

    def test_section_creation(self):
        """Test section creation"""
        section = Section.create(id="test", content="content")
        assert section.metadata.id == "test"
        assert section.content == "content"
        assert section.raw_content == "content"

    def test_section_serialization(self, basic_section):
        """Test section serialization"""
        data = basic_section.to_dict()
        restored = Section.from_dict(data)

        assert restored.metadata.id == basic_section.metadata.id
        assert restored.metadata.tags == basic_section.metadata.tags
        assert restored.content == basic_section.content
        assert restored.raw_content == basic_section.raw_content


class TestContainer:
    """Test container functionality"""

    @pytest.fixture
    def basic_container(self, basic_section):
        """Create basic container for testing"""
        container = Container.create()
        container.params = {"fmt": "json"}
        container.metadata = Metadata(id="container", tags=["test"])
        container.add_section(basic_section)
        return container

    def test_container_creation(self):
        """Test container creation"""
        container = Container.create()
        assert container.params == {}
        assert isinstance(container.metadata, Metadata)
        assert container.sections == []

    def test_section_management(self, basic_section):
        """Test section management"""
        container = Container.create()

        # Add section
        container.add_section(basic_section)
        assert len(container.sections) == 1

        # Get section
        section = container.get_section(basic_section.metadata.id)
        assert section == basic_section

        # Get nonexistent section
        assert container.get_section("nonexistent") is None

    def test_container_serialization(self, basic_container):
        """Test container serialization"""
        data = basic_container.to_dict()
        restored = Container.from_dict(data)

        assert restored.params == basic_container.params
        assert restored.metadata.id == basic_container.metadata.id
        assert len(restored.sections) == len(basic_container.sections)
        assert restored.sections[0].metadata.id == basic_container.sections[0].metadata.id

    def test_duplicate_section_prevention(self, basic_section):
        """Test prevention of duplicate sections"""
        container = Container.create()
        container.add_section(basic_section)
        container.add_section(basic_section)  # Try to add same section again
        assert len(container.sections) == 1


@pytest.mark.parametrize("create_fn,expected_type", [
    (Metadata, Metadata),
    (Section.create, Section),
    (Container.create, Container)
])
def test_factory_methods(create_fn, expected_type):
    """Test factory methods for types"""
    instance = create_fn()
    assert isinstance(instance, expected_type)


def test_inheritance_chain():
    """Test inheritance relationships"""
    metadata = Metadata()

    # MetadataParameters -> Metadata
    assert isinstance(metadata, MetadataParameters)

    # Default parameters inheritance
    assert hasattr(metadata, 'fmt')
    assert hasattr(metadata, 'enc')
    assert hasattr(metadata, 'crypt')
    assert hasattr(metadata, 'comp')
    assert hasattr(metadata, 'lang')
