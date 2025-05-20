import pytest

from flextag.flextag import FlexTag


class TestTags:
    @pytest.fixture
    def parser(self):
        return FlexTag()

    def test_tag_inheritance(self, parser):
        """Test tag inheritance from defaults"""
        content = """[[]]: defaults
[#default1 #default2 /]
[[/]]

[[#tag1 #tag2]]
content
[[/]]"""

        container = parser._parse_source(content, "<string>")
        section = container.sections[0]

        assert sorted(section.raw_tags) == sorted(["#tag1", "#tag2"])
        assert sorted(section.tags) == sorted(
            ["#default1", "#default2", "#tag1", "#tag2"]
        )
