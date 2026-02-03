import pytest

from flextag.flextag import FlexTag


class TestDefaults:
    @pytest.fixture
    def parser(self):
        return FlexTag()

    def test_default_metadata_inheritance(self, parser):
        """Test defaults metadata inheritance using ---meta--- block"""
        data = """---meta---
[[#default param="default_value"]]
---/meta---

[[#section]]
content
[[/]]"""

        container = parser._parse_source(data, "<string>")
        section = container.sections[0]

        # Section should inherit default tags from meta
        assert "#default" in container.tags
        assert "#section" in section.tags
        assert container.parameters["param"] == "default_value"

    def test_default_override(self, parser):
        """Test section overriding default metadata"""
        data = """---meta---
[[#default param="default_value" shared="keep"]]
---/meta---

[[#section param="override_value"]]
content
[[/]]"""

        container = parser._parse_source(data, "<string>")
        section = container.sections[0]

        # Container has defaults, section has its own
        assert "#default" in container.tags
        assert "#section" in section.tags

        # Container should have default params
        assert container.parameters["param"] == "default_value"
        assert container.parameters["shared"] == "keep"

        # Section should have its own override
        assert section.parameters["param"] == "override_value"

    def test_multiple_tags_in_meta(self, parser):
        """Test multiple tags in meta block"""
        data = """---meta---
[[#tag1 #tag2 param1="value1" param2="value2"]]
---/meta---

[[#section]]
content
[[/]]"""

        container = parser._parse_source(data, "<string>")

        assert "#tag1" in container.tags
        assert "#tag2" in container.tags
        assert container.parameters["param1"] == "value1"
        assert container.parameters["param2"] == "value2"
