import pytest
import flextag


class TestJSONWithFlexTag:
    """Test suite for JSON content type with FlexTag parsing."""

    def test_simple_json_parsing(self):
        """Test basic JSON parsing within FlexTag sections."""
        test_string = """
[[simple_config]]: json
{
    "name": "Simple Config",
    "debug": true,
    "port": 8080,
    "version": null
}
[[/simple_config]]
"""

        view = flextag.load(string=test_string)

        # Test section parsing
        assert len(view.sections) == 1
        section = view.sections[0]
        assert section.id == "simple_config"
        assert section.type_name == "json"

        # Test content parsing
        content = section.content
        assert isinstance(content, dict)
        assert content["name"] == "Simple Config"
        assert content["debug"] is True
        assert content["port"] == 8080
        assert content["version"] is None

        # Test dict conversion
        data = view.to_dict()
        assert data["simple_config"]["name"] == "Simple Config"

    def test_complex_json_structures(self):
        """Test complex nested JSON structures."""
        test_string = """
[[complex_config]]: json
{
    "app_name": "My App",
    "database": {
        "host": "localhost",
        "pool": {
            "max_connections": 50
        }
    },
    "servers": [
        {
            "name": "alpha",
            "ip": "10.0.0.1",
            "tags": ["web", "api"]
        },
        {
            "name": "beta",
            "ip": "10.0.0.2", 
            "tags": ["db", "cache"]
        }
    ]
}
[[/complex_config]]
"""

        view = flextag.load(string=test_string)
        data = view.to_dict()
        config = data["complex_config"]

        # Test nested object access
        assert config["app_name"] == "My App"
        assert config["database"]["host"] == "localhost"
        assert config["database"]["pool"]["max_connections"] == 50

        # Test array access
        assert len(config["servers"]) == 2
        assert config["servers"][0]["name"] == "alpha"
        assert config["servers"][1]["name"] == "beta"
        assert "web" in config["servers"][0]["tags"]
        assert "db" in config["servers"][1]["tags"]

    def test_json_with_brackets_in_strings(self):
        """Test JSON containing bracket characters that might confuse parser."""
        test_string = """
[[tricky_json]]: json
{
    "description": "This JSON contains [[double brackets]] in a string",
    "template": "Section: [[section_name]] goes here",
    "brackets": {
        "single": "[single]",
        "double": "[[double]]",
        "mixed": "[mixed] and [[also_mixed]]"
    },
    "arrays_with_brackets": [
        "[item1]",
        "[[item2]]",
        {"nested": "[[value]]"}
    ]
}
[[/tricky_json]]
"""

        view = flextag.load(string=test_string)
        data = view.to_dict()
        config = data["tricky_json"]

        # Verify bracket strings are preserved as content, not parsed as sections
        assert "[[double brackets]]" in config["description"]
        assert config["template"] == "Section: [[section_name]] goes here"
        assert config["brackets"]["single"] == "[single]"
        assert config["brackets"]["double"] == "[[double]]"
        assert config["arrays_with_brackets"][0] == "[item1]"
        assert config["arrays_with_brackets"][1] == "[[item2]]"
        assert config["arrays_with_brackets"][2]["nested"] == "[[value]]"

    def test_multiple_json_sections(self):
        """Test multiple JSON sections with same ID."""
        test_string = """
[[config]]: json
{
    "format": "json",
    "version": 1
}
[[/config]]

[[config]]: json
{
    "format": "json",
    "version": 2
}
[[/config]]
"""

        view = flextag.load(string=test_string)
        data = view.to_dict()

        # Multiple sections with same ID should become a list
        assert isinstance(data["config"], list)
        assert len(data["config"]) == 2
        assert data["config"][0]["version"] == 1
        assert data["config"][1]["version"] == 2

    def test_json_mixed_with_other_formats(self):
        """Test JSON sections alongside other format types."""
        test_string = """
[[config]]: json
{
    "format": "json",
    "data": ["item1", "item2"]
}
[[/config]]

[[config]]: yaml
format: yaml
data:
  - item3
  - item4
[[/config]]

[[summary]]: json
{
    "total_configs": 2,
    "formats": ["json", "yaml"]
}
[[/summary]]
"""

        view = flextag.load(string=test_string)
        data = view.to_dict()

        # Test mixed formats
        configs = data["config"]
        assert len(configs) == 2
        assert configs[0]["format"] == "json"
        assert configs[1]["format"] == "yaml"

        # Test summary section
        summary = data["summary"]
        assert summary["total_configs"] == 2
        assert "json" in summary["formats"]
        assert "yaml" in summary["formats"]

    def test_json_parsing_errors(self):
        """Test that invalid JSON raises appropriate errors."""
        invalid_json = """
[[bad_json]]: json
{
    "name": "test",
    "invalid": json syntax
}
[[/bad_json]]
"""

        view = flextag.load(string=invalid_json)

        # Should raise error when accessing content
        with pytest.raises(flextag.FlexTagSyntaxError) as exc_info:
            _ = view.sections[0].content

        assert "JSON parsing error" in str(exc_info.value)

    def test_empty_json_section(self):
        """Test empty JSON section behavior."""
        test_string = """
[[empty_json]]: json
[[/empty_json]]
"""

        view = flextag.load(string=test_string)
        section = view.sections[0]

        # Empty content should return empty string
        assert section.content == ""

    def test_json_data_types(self):
        """Test all JSON data types are properly parsed."""
        test_string = """
[[types_test]]: json
{
    "string": "text",
    "number_int": 42,
    "number_float": 3.14,
    "boolean_true": true,
    "boolean_false": false,
    "null_value": null,
    "array": [1, 2, 3],
    "object": {"nested": "value"}
}
[[/types_test]]
"""

        view = flextag.load(string=test_string)
        content = view.sections[0].content

        # Test all data types
        assert isinstance(content["string"], str)
        assert isinstance(content["number_int"], int)
        assert isinstance(content["number_float"], float)
        assert isinstance(content["boolean_true"], bool)
        assert isinstance(content["boolean_false"], bool)
        assert content["null_value"] is None
        assert isinstance(content["array"], list)
        assert isinstance(content["object"], dict)

        # Test values
        assert content["string"] == "text"
        assert content["number_int"] == 42
        assert content["number_float"] == 3.14
        assert content["boolean_true"] is True
        assert content["boolean_false"] is False
        assert content["array"] == [1, 2, 3]
        assert content["object"]["nested"] == "value"
