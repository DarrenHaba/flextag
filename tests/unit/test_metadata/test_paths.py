import pytest

from flextag.flextag import FlexTag


class TestPaths:
    @pytest.fixture
    def parser(self):
        return FlexTag()

    def test_path_inheritance(self, parser):
        """Test path inheritance from defaults"""
        content = """[[]]: defaults
[ @default.path1 @default.path2 /]
[[/]]

[[@path1 @path2]]
content
[[/]]"""

        container = parser._parse_source(content, "<string>")
        section = container.sections[0]

        assert sorted(section.raw_paths) == sorted(["@path1", "@path2"])
        expected = ["@default.path1", "@default.path2", "@path1", "@path2"]
        assert sorted(section.paths) == sorted(expected)
