import pytest

from flextag.flextag import FlexTag


class TestParameters:
    @pytest.fixture
    def parser(self):
        return FlexTag()

    def test_parameter_inheritance(self, parser):
        """Test parameter inheritance and overrides"""
        content = """[[]]: defaults
[default_param1="default1" default_param2="default2" shared="default" /]
[[/]]

[[shared="override" local="value"]]
content
[[/]]"""

        container = parser._parse_source(content, "<string>")
        section = container.sections[0]

        assert section.raw_parameters == {"shared": "override", "local": "value"}
        assert section.parameters == {
            "default_param1": "default1",
            "default_param2": "default2",
            "shared": "override",
            "local": "value",
        }

    @pytest.mark.parametrize(
        "param_str,expected_value,expected_type",
        [
            ("int_param=42", 42, int),
            ("float_param=3.14", 3.14, float),
            ('str_param="hello"', "hello", str),
            ("bool_param=true", True, bool),
            ("bool_param=false", False, bool),
            ("null_param=null", None, type(None)),
        ],
    )
    def test_parameter_type_conversion(
        self, parser, param_str, expected_value, expected_type
    ):
        """Test parameter type conversion for different formats"""
        data = f"""[[section {param_str}]]
content
[[/section]]"""

        container = parser._parse_source(data, "<string>")
        section = container.sections[0]

        param_name = param_str.split("=")[0]
        assert section.parameters[param_name] == expected_value
        assert isinstance(section.parameters[param_name], expected_type)

    def test_multiple_parameter_types(self, parser):
        """Test parsing multiple parameters with different types"""
        data = """[[section int_param=42 float_param=3.14 str_param="hello" bool_param=true null_param=null]]
content
[[/section]]"""

        container = parser._parse_source(data, "<string>")
        section = container.sections[0]

        assert section.parameters == {
            "int_param": 42,
            "float_param": 3.14,
            "str_param": "hello",
            "bool_param": True,
            "null_param": None,
        }

    def test_parameter_edge_cases(self, parser):
        """Test parameter parsing edge cases"""
        data = """[[section empty="" spaces="  spaced  " quotes='"quoted"' /]]"""

        container = parser._parse_source(data, "<string>")
        section = container.sections[0]

        assert section.parameters["empty"] == ""
        assert section.parameters["spaces"] == "  spaced  "
        assert section.parameters["quotes"] == '"quoted"'

    def test_parameter_type_edge_cases(self, parser):
        """Test parameter parsing for white space around boolean, null, int, and float values"""
        data = """[[section bool_true=true    null_val=null    int_val=123    float_val=1.23  /]]"""
        container = parser._parse_source(data, "<string>")
        section = container.sections[0]

        # Check that extra spaces are properly trimmed and type conversion is performed.
        assert section.parameters["bool_true"] is True
        assert section.parameters["null_val"] is None
        assert section.parameters["int_val"] == 123
        assert section.parameters["float_val"] == 1.23

    def test_parameter_split_edge_cases(self, parser):
        """Test parameter parsing for white space around boolean, null, int, and float values"""
        data = """[[section bool_true="true"    null_val="null"    int_val=123    float_val=1.23  /]]"""
        container = parser._parse_source(data, "<string>")
        section = container.sections[0]

        # Check that extra spaces are properly trimmed and type conversion is performed.
        assert section.parameters["bool_true"] is True
        assert section.parameters["null_val"] is None
        assert section.parameters["int_val"] == 123
        assert section.parameters["float_val"] == 1.23
