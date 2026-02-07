import pytest

from flextag.flextag import FlexTag


class TestDefaults:
    @pytest.fixture
    def parser(self):
        return FlexTag()

    def test_default_metadata_inheritance(self, parser):
        """Test file-metadata tags are promoted to container level"""
        data = """[[#default param="default_value"]]: file-metadata
[[/]]

[[#section]]
content
[[/]]"""

        container = parser._parse_source(data, "<string>")
        section = container.sections[0]

        # Container should have tags from file-metadata
        assert "#default" in container.tags
        assert "#section" in section.tags
        assert container.parameters["param"] == "default_value"

    def test_default_override(self, parser):
        """Test section params are independent from file-metadata params"""
        data = """[[#default param="default_value" shared="keep"]]: file-metadata
[[/]]

[[#section param="override_value"]]
content
[[/]]"""

        container = parser._parse_source(data, "<string>")
        section = container.sections[0]

        # Container has file-metadata tags/params
        assert "#default" in container.tags
        assert "#section" in section.tags

        # Container should have file-metadata params
        assert container.parameters["param"] == "default_value"
        assert container.parameters["shared"] == "keep"

        # Section should have its own params
        assert section.parameters["param"] == "override_value"

    def test_multiple_tags_in_meta(self, parser):
        """Test multiple tags in file-metadata section"""
        data = """[[#tag1 #tag2 param1="value1" param2="value2"]]: file-metadata
[[/]]

[[#section]]
content
[[/]]"""

        container = parser._parse_source(data, "<string>")

        assert "#tag1" in container.tags
        assert "#tag2" in container.tags
        assert container.parameters["param1"] == "value1"
        assert container.parameters["param2"] == "value2"
