import pytest
import json
from flextag.core.parsers.content import TextParser, JSONParser, YAMLParser
from flextag.core.parsers.metadata import MetadataParser
from flextag.core.parsers.parsers import SectionParser, ContainerParser
from flextag.exceptions import FlexTagError


class TestContentParsers:
    """Test content format parsers"""

    @pytest.fixture
    def text_parser(self):
        return TextParser()

    @pytest.fixture
    def json_parser(self):
        return JSONParser()

    @pytest.fixture
    def yaml_parser(self):
        return YAMLParser()

    def test_text_parser(self, text_parser):
        """Test text parser handles basic text"""
        content = "Hello\nWorld"
        assert text_parser.parse(content) == "Hello\nWorld"
        assert text_parser.dump("Test") == "Test"

    def test_json_parser_valid(self, json_parser):
        """Test JSON parser with valid content"""
        data = {
            "name": "test",
            "value": 42,
            "nested": {"key": "value"}
        }
        content = json.dumps(data)
        parsed = json_parser.parse(content)
        assert parsed == data
        assert json.loads(json_parser.dump(data)) == data

    def test_json_parser_invalid(self, json_parser):
        """Test JSON parser with invalid content"""
        with pytest.raises(FlexTagError):
            json_parser.parse("{invalid json}")

    def test_yaml_parser_valid(self, yaml_parser):
        """Test YAML parser with valid content"""
        content = """
        name: test
        value: 42
        nested:
          key: value
        """
        parsed = yaml_parser.parse(content)
        assert parsed["name"] == "test"
        assert parsed["value"] == 42
        assert parsed["nested"]["key"] == "value"

        # Test round-trip
        dumped = yaml_parser.dump(parsed)
        assert yaml_parser.parse(dumped) == parsed

    def test_yaml_parser_invalid(self, yaml_parser):
        """Test YAML parser with invalid content"""
        with pytest.raises(FlexTagError):
            yaml_parser.parse("""
    first: value
        way:
            too:
              indented: here
    """)

    def test_empty_content(self, json_parser, yaml_parser):
        """Test parsers handle empty content"""
        assert json_parser.parse("") == {}
        assert yaml_parser.parse("") == {}


class TestMetadataParser:
    """Test metadata header parsing"""

    @pytest.fixture
    def metadata_parser(self):
        return MetadataParser()

    def test_parse_params(self, metadata_parser):
        """Test parsing PARAMS header"""
        header = '[[PARAMS fmt="json" enc="utf-8" custom="value"]]'
        params = metadata_parser.parse_params(header)
        assert params["fmt"] == "json"
        assert params["enc"] == "utf-8"
        assert params["custom"] == "value"

    def test_parse_meta(self, metadata_parser):
        """Test parsing META header"""
        header = '[[META:config #system #db .sys.config version="1.0"]]'
        meta = metadata_parser.parse_meta(header)
        assert meta.id == "config"
        assert "system" in meta.tags
        assert "db" in meta.tags
        assert "sys.config" in meta.paths
        assert meta.parameters["version"] == 1.0  # Updated assertion

    def test_parse_section_meta(self, metadata_parser):
        """Test parsing section header"""
        header = '[[SEC:data #user .data.users active=true count=42]]'
        meta = metadata_parser.parse_section_meta(header)
        assert meta.id == "data"
        assert "user" in meta.tags
        assert "data.users" in meta.paths
        assert meta.parameters["active"] is True
        assert meta.parameters["count"] == 42

    def test_invalid_headers(self, metadata_parser):
        """Test handling invalid headers"""
        invalid_headers = [
            "[[INVALID]]",             # Invalid header type
            "[[PARAMS invalid=]]",     # Missing parameter value
            "[[PARAMS:id invalid=]]",  # ID not allowed in PARAMS
            "[[META:#invalid]]",       # Invalid ID (starts with '#')
        ]
        for header in invalid_headers:
            with pytest.raises(FlexTagError):
                if header.startswith('[[PARAMS'):
                    metadata_parser.parse_params(header)
                elif header.startswith('[[META'):
                    metadata_parser.parse_meta(header)
                elif header.startswith('[[SEC'):
                    metadata_parser.parse_section_meta(header)
                else:
                    # General invalid header
                    metadata_parser.parse_header(header)

class TestSectionParser:
    """Test section parsing"""

    @pytest.fixture
    def section_parser(self):
        return SectionParser()

    @pytest.fixture
    def json_parser(self):
        return JSONParser()

    def test_parse_basic_section(self, section_parser):
        """Test parsing basic section"""
        content = """[[SEC:config #system .config fmt="text"]]
This is test content
[[/SEC]]"""
        section = section_parser.parse(content)
        assert section.metadata.id == "config"
        assert "system" in section.metadata.tags
        assert "config" in section.metadata.paths
        assert section.content == "This is test content"

    def test_parse_json_section(self, section_parser, json_parser):
        """Test parsing section with JSON content"""
        content = '''[[SEC:data #api .data.users fmt="json"]]
{
  "users": ["user1", "user2"],
  "active": true
}
[[/SEC]]'''
        section = section_parser.parse(content, json_parser)
        assert section.metadata.id == "data"
        assert isinstance(section.content, dict)
        assert section.content["users"] == ["user1", "user2"]

    def test_section_roundtrip(self, section_parser, json_parser):
        """Test section serialization roundtrip"""
        original = '''[[SEC:config #system fmt="json"]]
{"port": 8080}
[[/SEC]]'''
        section = section_parser.parse(original, json_parser)
        dumped = section_parser.dump(section, json_parser)
        reparsed = section_parser.parse(dumped, json_parser)
        assert reparsed.metadata.id == section.metadata.id
        assert reparsed.metadata.tags == section.metadata.tags
        assert reparsed.content == section.content


class TestContainerParser:
    """Test container parsing"""

    @pytest.fixture
    def container_parser(self):
        parser = ContainerParser()
        parser.register_content_parser("json", JSONParser())
        parser.register_content_parser("yaml", YAMLParser())
        parser.register_content_parser("text", TextParser())
        return parser

    def test_parse_full_container(self, container_parser):
        """Test parsing complete container"""
        content = '''[[PARAMS fmt="text" enc="utf-8"]]
[[META:config #prod .sys.config version=1.0]]
[[SEC:db #database .sys.db fmt="json"]]
{
    "port": 5432,
    "host": "localhost"
}
[[/SEC]]
[[SEC:api #service .sys.api fmt="yaml"]]
port: 8080
host: localhost
[[/SEC]]'''

        container = container_parser.parse(content)

        # Check params
        assert container.params["fmt"] == "text"
        assert container.params["enc"] == "utf-8"

        # Check metadata
        assert container.metadata.id == "config"
        assert "prod" in container.metadata.tags
        assert "sys.config" in container.metadata.paths
        assert container.metadata.parameters["version"] == 1.0

        # Check sections
        assert len(container.sections) == 2

        # Check DB section
        db_section = container.sections[0]
        assert db_section.metadata.id == "db"
        assert "database" in db_section.metadata.tags
        assert isinstance(db_section.content, dict)
        assert db_section.content["port"] == 5432

        # Check API section
        api_section = container.sections[1]
        assert api_section.metadata.id == "api"
        assert "service" in api_section.metadata.tags
        assert isinstance(api_section.content, dict)
        assert api_section.content["port"] == 8080

    def test_container_roundtrip(self, container_parser):
        """Test container serialization roundtrip"""
        original = '''[[PARAMS fmt="json"]]
[[META:test #tag]]
[[SEC:data fmt="json"]]
{"value": 42}
[[/SEC]]'''

        container = container_parser.parse(original)
        dumped = container_parser.dump(container)
        reparsed = container_parser.parse(dumped)

        assert reparsed.params == container.params
        assert reparsed.metadata.id == container.metadata.id
        assert reparsed.metadata.tags == container.metadata.tags
        assert len(reparsed.sections) == len(container.sections)
        assert reparsed.sections[0].content == container.sections[0].content

    def test_params_with_empty_values(self, metadata_parser):
        """Test parsing PARAMS header with empty values for crypt, comp, lang"""
        header = '[[PARAMS fmt="json" enc="utf-8" crypt="" comp="" lang=""]]'
        params = metadata_parser.parse_params(header)
        assert params["fmt"] == "json"
        assert params["enc"] == "utf-8"
        assert params["crypt"] == ""
        assert params["comp"] == ""
        assert params["lang"] == ""

    def test_invalid_container(self, container_parser):
        """Test handling invalid containers"""
        invalid_containers = [
            # Missing section end marker
            '''[[SEC:test]]
content''',

            # Invalid JSON in section
            '''[[SEC:test fmt="json"]]
{invalid json}
[[/SEC]]''',

            # Invalid YAML in section
            '''[[SEC:test fmt="yaml"]]
invalid: yaml:
  - bad indent
[[/SEC]]'''
        ]

        for content in invalid_containers:
            with pytest.raises(FlexTagError):
                container_parser.parse(content)

    def test_empty_sections(self, container_parser):
        """Test handling empty sections"""
        content = '''[[PARAMS fmt="json"]]
[[SEC:empty fmt="json"]]
[[/SEC]]'''

        container = container_parser.parse(content)
        assert len(container.sections) == 1
        assert container.sections[0].content == {}

    @pytest.mark.parametrize("fmt,content,expected", [
        ("json", '{"key":"value"}', {"key": "value"}),
        ("yaml", "key: value", {"key": "value"}),
        ("text", "plain text", "plain text")
    ])
    def test_format_handling(self, container_parser, fmt, content, expected):
        """Test handling different content formats"""
        container_str = f'''[[SEC:test fmt="{fmt}"]]
{content}
[[/SEC]]'''

        container = container_parser.parse(container_str)
        assert container.sections[0].content == expected
