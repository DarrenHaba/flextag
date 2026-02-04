import pytest

from flextag.flextag import FlexTag


class TestTags:
    @pytest.fixture
    def parser(self):
        return FlexTag()

    def test_tag_inheritance(self, parser):
        """Test tag inheritance from defaults"""
        content = """[[]]: defaults
[ #default.path1 #default.path2 /]
[[/]]

[[#path1 #path2]]
content
[[/]]"""

        container = parser._parse_source(content, "<string>")
        section = container.sections[0]

        assert sorted(section.raw_tags) == sorted(["#path1", "#path2"])
        expected = ["#default.path1", "#default.path2", "#path1", "#path2"]
        assert sorted(section.tags) == sorted(expected)
