import pytest
import flextag


class TestYAMLWithFlexTag:
    """Test suite for YAML content type with FlexTag parsing."""

    def test_simple_yaml_parsing(self):
        """Test basic YAML parsing within FlexTag sections."""
        test_string = """
[[simple_config]]: yaml
name: "Simple Config"
debug: true
port: 8080
version: null
[[/simple_config]]
"""

        view = flextag.load(string=test_string)

        # Test section parsing
        assert len(view.sections) == 1
        section = view.sections[0]
        assert section.id == "simple_config"
        assert section.type_name == "yaml"

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

    def test_complex_yaml_structures(self):
        """Test complex nested YAML structures."""
        test_string = """
[[complex_config]]: yaml
app_name: "My App"
database:
  host: localhost
  port: 5432
  pool:
    max_connections: 50

servers:
  - name: alpha
    ip: 10.0.0.1
    tags:
      - web
      - api
  - name: beta
    ip: 10.0.0.2
    tags:
      - db
      - cache

api:
  version: v2
  endpoints:
    - users
    - posts
[[/complex_config]]
"""

        view = flextag.load(string=test_string)
        data = view.to_dict()
        config = data["complex_config"]

        # Test nested object access
        assert config["app_name"] == "My App"
        assert config["database"]["host"] == "localhost"
        assert config["database"]["port"] == 5432
        assert config["database"]["pool"]["max_connections"] == 50

        # Test array access
        assert len(config["servers"]) == 2
        assert config["servers"][0]["name"] == "alpha"
        assert config["servers"][1]["name"] == "beta"
        assert "web" in config["servers"][0]["tags"]
        assert "db" in config["servers"][1]["tags"]
        assert config["api"]["version"] == "v2"
        assert "users" in config["api"]["endpoints"]

    def test_yaml_with_brackets_in_strings(self):
        """Test YAML containing bracket characters that might confuse parser."""
        test_string = """
[[tricky_yaml]]: yaml
description: "This YAML contains [[double brackets]] in a string"
template: "Section: [[section_name]] goes here"

brackets:
  single: "[single]"
  double: "[[double]]"
  mixed: "[mixed] and [[also_mixed]]"

arrays_with_brackets:
  - "[item1]"
  - "[[item2]]"
  - nested: "[[value]]"
[[/tricky_yaml]]
"""

        view = flextag.load(string=test_string)
        data = view.to_dict()
        config = data["tricky_yaml"]

        # Verify bracket strings are preserved as content, not parsed as sections
        assert "[[double brackets]]" in config["description"]
        assert config["template"] == "Section: [[section_name]] goes here"
        assert config["brackets"]["single"] == "[single]"
        assert config["brackets"]["double"] == "[[double]]"
        assert config["arrays_with_brackets"][0] == "[item1]"
        assert config["arrays_with_brackets"][1] == "[[item2]]"
        assert config["arrays_with_brackets"][2]["nested"] == "[[value]]"

    def test_yaml_multiline_strings(self):
        """Test YAML multiline strings with brackets."""
        test_string = """
[[multiline_test]]: yaml
# Literal block scalar
literal: |
  This is a multiline string
  with [[brackets]] inside
  and even [[multiple]] [[brackets]]
  on the same line.

# Folded style
folded: >
  This is a folded string
  with [[brackets]] that should
  be treated as regular text.
[[/multiline_test]]
"""

        view = flextag.load(string=test_string)
        data = view.to_dict()
        config = data["multiline_test"]

        # Test multiline string content
        assert "[[brackets]]" in config["literal"]
        assert "[[multiple]]" in config["literal"]
        assert "multiline string" in config["literal"]
        assert "[[brackets]] that should" in config["folded"]

    def test_yaml_anchors_and_aliases(self):
        """Test YAML anchors and aliases functionality."""
        test_string = """
[[yaml_features]]: yaml
# YAML anchors and aliases
defaults: &defaults
  timeout: 30
  retries: 3

production:
  <<: *defaults
  host: prod.example.com
  debug: false

development:
  <<: *defaults
  host: dev.example.com
  debug: true
[[/yaml_features]]
"""

        view = flextag.load(string=test_string)
        data = view.to_dict()
        config = data["yaml_features"]

        # Test anchor/alias functionality
        assert config["defaults"]["timeout"] == 30
        assert config["defaults"]["retries"] == 3

        # Test that aliases properly inherit values
        assert config["production"]["timeout"] == 30  # inherited
        assert config["production"]["retries"] == 3  # inherited
        assert config["production"]["host"] == "prod.example.com"
        assert config["production"]["debug"] is False

        assert config["development"]["timeout"] == 30  # inherited
        assert config["development"]["debug"] is True

    def test_yaml_data_types(self):
        """Test YAML data type parsing."""
        test_string = """
[[types_test]]: yaml
string: "text"
integer: 42
float: 3.14
boolean_true: true
boolean_false: false
null_value: null
date: 2023-12-25
list:
  - item1
  - item2
  - item3
mapping:
  key1: value1
  key2: value2
[[/types_test]]
"""

        view = flextag.load(string=test_string)
        content = view.sections[0].content

        # Test data types
        assert isinstance(content["string"], str)
        assert isinstance(content["integer"], int)
        assert isinstance(content["float"], float)
        assert isinstance(content["boolean_true"], bool)
        assert isinstance(content["boolean_false"], bool)
        assert content["null_value"] is None
        assert isinstance(content["list"], list)
        assert isinstance(content["mapping"], dict)

        # Test values
        assert content["string"] == "text"
        assert content["integer"] == 42
        assert content["float"] == 3.14
        assert content["boolean_true"] is True
        assert content["boolean_false"] is False
        assert len(content["list"]) == 3
        assert content["mapping"]["key1"] == "value1"

    def test_multiple_yaml_sections(self):
        """Test multiple YAML sections with same ID."""
        test_string = """
[[config]]: yaml
format: yaml
version: 1
[[/config]]

[[config]]: yaml
format: yaml
version: 2
[[/config]]
"""

        view = flextag.load(string=test_string)
        data = view.to_dict()

        # Multiple sections with same ID should become a list
        assert isinstance(data["config"], list)
        assert len(data["config"]) == 2
        assert data["config"][0]["version"] == 1
        assert data["config"][1]["version"] == 2

    def test_yaml_mixed_with_other_formats(self):
        """Test YAML sections alongside other format types."""
        test_string = """
[[config]]: yaml
format: yaml
data:
  - item1
  - item2
[[/config]]

[[config]]: json
{
    "format": "json",
    "data": ["item3", "item4"]
}
[[/config]]

[[summary]]: yaml
total_configs: 2
formats:
  - yaml
  - json
[[/summary]]
"""

        view = flextag.load(string=test_string)
        data = view.to_dict()

        # Test mixed formats
        configs = data["config"]
        assert len(configs) == 2
        assert configs[0]["format"] == "yaml"
        assert configs[1]["format"] == "json"

        # Test summary section
        summary = data["summary"]
        assert summary["total_configs"] == 2
        assert "yaml" in summary["formats"]
        assert "json" in summary["formats"]

    def test_yaml_parsing_errors(self):
        """Test that invalid YAML raises appropriate errors."""
        invalid_yaml = """
[[bad_yaml]]: yaml
name: "test"
invalid yaml: [unclosed bracket
  - item
[[/bad_yaml]]
"""

        view = flextag.load(string=invalid_yaml)

        # Should raise error when accessing content
        with pytest.raises(flextag.FlexTagSyntaxError) as exc_info:
            _ = view.sections[0].content

        assert "YAML parsing error" in str(exc_info.value)

    def test_empty_yaml_section(self):
        """Test empty YAML section behavior."""
        test_string = """
[[empty_yaml]]: yaml
[[/empty_yaml]]
"""

        view = flextag.load(string=test_string)
        section = view.sections[0]

        # Empty content should return empty string
        assert section.content == ""

    def test_yaml_comments_preserved_in_structure(self):
        """Test that YAML structure is maintained despite comments."""
        test_string = """
[[commented_yaml]]: yaml
# This is a comment
name: "Config"
# Another comment
settings:
  # Nested comment
  debug: true
  # Final comment
  port: 8080
[[/commented_yaml]]
"""

        view = flextag.load(string=test_string)
        content = view.sections[0].content

        # Comments should not affect parsing
        assert content["name"] == "Config"
        assert content["settings"]["debug"] is True
        assert content["settings"]["port"] == 8080
