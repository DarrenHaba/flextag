import pytest
import flextag


class TestTOMLWithFlexTag:
    """Test suite for TOML content type with FlexTag parsing."""

    def test_simple_toml_parsing(self):
        """Test basic TOML parsing within FlexTag sections."""
        test_string = """
[[simple_config]]: toml
name = "Simple Config"
debug = true
port = 8080
[[/simple_config]]
"""

        view = flextag.load(string=test_string)

        # Test section parsing
        assert len(view.sections) == 1
        section = view.sections[0]
        assert section.id == "simple_config"
        assert section.type_name == "toml"

        # Test content parsing
        content = section.content
        assert isinstance(content, dict)
        assert content["name"] == "Simple Config"
        assert content["debug"] is True
        assert content["port"] == 8080

        # Test dict conversion
        data = view.to_dict()
        assert data["simple_config"]["name"] == "Simple Config"

    def test_complex_toml_structures(self):
        """Test complex nested TOML structures with tables."""
        test_string = """
[[complex_config]]: toml
app_name = "My App"
version = "1.0.0"

# Regular table
[database]
host = "localhost"
port = 5432
enabled = true

# Nested table
[database.pool]
max_connections = 50
timeout = 30

# Array of tables (this is where [[]] syntax appears in TOML)
[[servers]]
name = "alpha"
ip = "10.0.0.1"
datacenter = "east"

[[servers]]
name = "beta"
ip = "10.0.0.2"
datacenter = "west"

# More complex nested structures
[api]
version = "v2"
endpoints = ["users", "posts", "comments"]

[api.auth]
method = "jwt"
expiry = 3600
[[/complex_config]]
"""

        view = flextag.load(string=test_string)
        data = view.to_dict()
        config = data["complex_config"]

        # Test basic values
        assert config["app_name"] == "My App"
        assert config["version"] == "1.0.0"

        # Test regular tables
        assert config["database"]["host"] == "localhost"
        assert config["database"]["port"] == 5432
        assert config["database"]["enabled"] is True

        # Test nested tables
        assert config["database"]["pool"]["max_connections"] == 50
        assert config["database"]["pool"]["timeout"] == 30

        # Test array of tables (TOML [[servers]] syntax)
        assert len(config["servers"]) == 2
        assert config["servers"][0]["name"] == "alpha"
        assert config["servers"][0]["ip"] == "10.0.0.1"
        assert config["servers"][0]["datacenter"] == "east"
        assert config["servers"][1]["name"] == "beta"
        assert config["servers"][1]["datacenter"] == "west"

        # Test nested structures
        assert config["api"]["version"] == "v2"
        assert "users" in config["api"]["endpoints"]
        assert config["api"]["auth"]["method"] == "jwt"
        assert config["api"]["auth"]["expiry"] == 3600

    def test_toml_tables_vs_flextag_sections(self):
        """Test that TOML [[table]] syntax doesn't interfere with FlexTag [[section]] syntax."""
        test_string = """
[[toml_with_tables]]: toml
title = "TOML with Array of Tables"

# This uses TOML's [[]] syntax for array of tables
[[products]]
name = "Hammer"
sku = 738594937

[[products]]
name = "Nail"
sku = 284758393
color = "gray"

# Another array of tables
[[database.servers]]
name = "server1"
ip = "192.168.1.1"

[[database.servers]]
name = "server2"
ip = "192.168.1.2"
[[/toml_with_tables]]
"""

        view = flextag.load(string=test_string)
        data = view.to_dict()
        config = data["toml_with_tables"]

        # Verify TOML array of tables worked correctly
        assert config["title"] == "TOML with Array of Tables"

        # Test products array of tables
        assert len(config["products"]) == 2
        assert config["products"][0]["name"] == "Hammer"
        assert config["products"][0]["sku"] == 738594937
        assert config["products"][1]["name"] == "Nail"
        assert config["products"][1]["color"] == "gray"

        # Test nested array of tables
        assert len(config["database"]["servers"]) == 2
        assert config["database"]["servers"][0]["name"] == "server1"
        assert config["database"]["servers"][1]["ip"] == "192.168.1.2"

    def test_toml_with_brackets_in_strings(self):
        """Test TOML containing bracket characters that might confuse parser."""
        test_string = """
[[tricky_toml]]: toml
# This TOML contains text that might confuse the parser
description = "This contains [[double brackets]] in a string"
# Use literal strings to avoid escaping issues
regex_pattern = '\\[\\[.*\\]\\]'

# Array of tables with bracket content
[[nested.items]]
value = "first"
comment = "Contains [[brackets]] in comment"

[[nested.items]]
value = "second"  
comment = "Another [[bracket]] example"
[[/tricky_toml]]
"""

        view = flextag.load(string=test_string)
        data = view.to_dict()
        config = data["tricky_toml"]

        # Verify bracket strings are preserved as content
        assert "[[double brackets]]" in config["description"]
        assert config["regex_pattern"] == r"\[\[.*\]\]"

        # Test nested array of tables with brackets in content
        assert len(config["nested"]["items"]) == 2
        assert config["nested"]["items"][0]["value"] == "first"
        assert "[[brackets]]" in config["nested"]["items"][0]["comment"]
        assert config["nested"]["items"][1]["value"] == "second"
        assert "[[bracket]]" in config["nested"]["items"][1]["comment"]

    def test_toml_data_types(self):
        """Test TOML data type parsing."""
        test_string = '''
[[types_test]]: toml
# String types
basic_string = "I'm a string"
literal_string = 'C:\\Users\\nodejs\\templates'
multiline_basic = """
Roses are red
Violets are blue"""

# Number types  
integer = 42
float_num = 3.14
infinity = inf
not_a_number = nan

# Boolean
bool_true = true
bool_false = false

# Datetime
date_time = 1979-05-27T07:32:00Z
local_date = 1979-05-27

# Arrays
simple_array = [1, 2, 3]
mixed_array = ["red", "yellow", "green"]
nested_array = [[1, 2], [3, 4, 5]]

# Inline tables
inline_table = { x = 1, y = 2 }
[[/types_test]]
'''

        view = flextag.load(string=test_string)
        content = view.sections[0].content

        # Test string types
        assert content["basic_string"] == "I'm a string"
        assert content["literal_string"] == r"C:\Users\nodejs\templates"
        assert "Roses are red" in content["multiline_basic"]

        # Test number types
        assert content["integer"] == 42
        assert content["float_num"] == 3.14
        assert content["infinity"] == float("inf")
        assert str(content["not_a_number"]) == "nan"

        # Test boolean
        assert content["bool_true"] is True
        assert content["bool_false"] is False

        # Test arrays
        assert content["simple_array"] == [1, 2, 3]
        assert "red" in content["mixed_array"]
        assert content["nested_array"] == [[1, 2], [3, 4, 5]]

        # Test inline table
        assert content["inline_table"]["x"] == 1
        assert content["inline_table"]["y"] == 2

    def test_multiple_toml_sections(self):
        """Test multiple TOML sections with same ID."""
        test_string = """
[[config]]: toml
format = "toml"
version = 1
[[/config]]

[[config]]: toml
format = "toml"
version = 2
[[/config]]
"""

        view = flextag.load(string=test_string)
        data = view.to_dict()

        # Multiple sections with same ID should become a list
        assert isinstance(data["config"], list)
        assert len(data["config"]) == 2
        assert data["config"][0]["version"] == 1
        assert data["config"][1]["version"] == 2

    def test_toml_mixed_with_other_formats(self):
        """Test TOML sections alongside other format types."""
        test_string = """
[[config]]: toml
format = "toml"
data = ["item1", "item2"]
[[/config]]

[[config]]: yaml
format: yaml
data:
  - item3
  - item4
[[/config]]

[[summary]]: toml
total_configs = 2
formats = ["toml", "yaml"]
[[/summary]]
"""

        view = flextag.load(string=test_string)
        data = view.to_dict()

        # Test mixed formats
        configs = data["config"]
        assert len(configs) == 2
        assert configs[0]["format"] == "toml"
        assert configs[1]["format"] == "yaml"

        # Test summary section
        summary = data["summary"]
        assert summary["total_configs"] == 2
        assert "toml" in summary["formats"]
        assert "yaml" in summary["formats"]

    def test_toml_parsing_errors(self):
        """Test that invalid TOML raises appropriate errors."""
        invalid_toml = """
[[bad_toml]]: toml
name = "test"
invalid = toml syntax
[[/bad_toml]]
"""

        view = flextag.load(string=invalid_toml)

        # Should raise error when accessing content
        with pytest.raises(flextag.FlexTagSyntaxError) as exc_info:
            _ = view.sections[0].content

        assert "TOML parsing error" in str(exc_info.value)

    def test_empty_toml_section(self):
        """Test empty TOML section behavior."""
        test_string = """
[[empty_toml]]: toml
[[/empty_toml]]
"""

        view = flextag.load(string=test_string)
        section = view.sections[0]

        # Empty content should return empty string
        assert section.content == ""

    def test_toml_comments_and_whitespace(self):
        """Test that TOML correctly handles comments and whitespace."""
        test_string = """
[[commented_toml]]: toml
# This is a comment
name = "Config"

# Another comment
[settings]
# Nested comment
debug = true
# Final comment
port = 8080

[[products]]
name = "Product 1"
# Comment in array of tables
[[/commented_toml]]
"""

        view = flextag.load(string=test_string)
        content = view.sections[0].content

        # Comments should not affect parsing
        assert content["name"] == "Config"
        assert content["settings"]["debug"] is True
        assert content["settings"]["port"] == 8080
        assert len(content["products"]) == 1
        assert content["products"][0]["name"] == "Product 1"
