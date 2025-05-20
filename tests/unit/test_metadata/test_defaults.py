import pytest

from flextag.flextag import FlexTag


class TestDefaults:
    @pytest.fixture
    def parser(self):
        return FlexTag()

    def test_default_metadata_inheritance(self, parser):
        """Test defaults metadata inheritance"""
        data = """[[]]: defaults
[#default param="default_value"]
[[/]]

[[section #section]]
content
[[/section]]"""

        container = parser._parse_source(data, "<string>")
        section = container.sections[0]

        # Section should inherit default params
        assert "#default" in section.tags
        assert "#section" in section.tags
        assert section.parameters["param"] == "default_value"

    def test_default_override(self, parser):
        """Test section overriding default metadata"""
        data = """[[]]: defaults
[#default param="default_value" shared="keep"]
[[/]]

[[section #section param="override_value"]]
content
[[/section]]"""

        container = parser._parse_source(data, "<string>")
        section = container.sections[0]

        # Verify tags inherited and combined
        assert "#default" in section.tags
        assert "#section" in section.tags

        # Section should override default param but keep others
        assert section.parameters["param"] == "override_value"  # Overridden
        assert section.parameters["shared"] == "keep"  # Inherited

    def test_multiple_default_lines(self, parser):
        """Test multiple metadata lines in defaults section"""
        data = """[[]]: defaults
[#tag1 param1="value1"
#tag2 
param2="value2"]
[[/]]

[[section]]
content
[[/section]]"""

        container = parser._parse_source(data, "<string>")
        section = container.sections[0]

        assert "#tag1" in section.tags
        assert "#tag2" in section.tags
        assert section.parameters["param1"] == "value1"
        assert section.parameters["param2"] == "value2"
