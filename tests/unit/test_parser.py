import pytest

from flextag.flextag import FlexParser, FlexTag, FlexTagSyntaxError


class TestFlexParser:
    """Test the basic parsing functionality"""

    @pytest.fixture
    def parser(self):
        return FlexParser()

    def test_basic_section_parsing(self, parser):
        """Test parsing a simple section with just a tag"""
        content = """[[#simple]]
        Basic content
        [[/]]"""

        result = parser.parse_bracket_sections(content.splitlines(), "<string>")
        sections = result["sections"]
        assert len(sections) == 1
        assert "#simple" in sections[0]["tags"]
        assert "Basic content" in sections[0]["raw_content"]

    def test_basic_section_parsing_params(self, parser):
        """Test basic section parsing with metadata"""
        content = """[[#tag1 #tag2 key="value"]]
    content
    [[/]]"""

        result = parser.parse_bracket_sections(content.splitlines(), "<string>")
        sections = result["sections"]
        assert len(sections) == 1
        section = sections[0]

        assert sorted(section["tags"]) == sorted(["#tag1", "#tag2"])
        assert section["params"] == {"key": "value"}
        assert "content" in section["raw_content"]

    def test_section_with_metadata(self, parser):
        """Test parsing a section with tags, paths, and params"""
        content = """[[#draft @path key=value]]
        Content
        [[/]]"""

        result = parser.parse_bracket_sections(content.splitlines(), "<string>")
        sections = result["sections"]
        assert sections[0]["tags"] == ["#draft", "#path"]
        assert sections[0]["params"] == {"key": "value"}

    def test_section_with_comment(self, parser):
        """Test parsing a section with comments between sections"""
        content = """
        # This is a valid comment.
        [[#test]]
        Content
        [[/]]"""

        result = parser.parse_bracket_sections(content.splitlines(), "<string>")
        sections = result["sections"]
        assert len(sections) == 1
        assert "Content" in sections[0]["raw_content"]

    def test_section_with_invalid_comment(self, parser):
        """Test that non-comment lines between sections raise FlexTagSyntaxError"""
        content = """
        This is an invalid comment
        [[#test]]
        Content
        [[/]]"""

        with pytest.raises(FlexTagSyntaxError) as excinfo:
            parser.parse_bracket_sections(content.splitlines(), "<string>")

        error_msg = str(excinfo.value)
        assert "<string> L2" in error_msg
        assert "Lines between sections must be comments starting with #" in error_msg

    def test_empty_content(self, parser):
        """Test handling of empty content sections"""
        content = """[[#tag]]
[[/]]"""
        result = parser.parse_bracket_sections(content.splitlines(), "<string>")
        sections = result["sections"]
        assert sections[0]["raw_content"] == ""

    def test_self_closing_section(self, parser):
        """Test self-closing tag syntax"""
        content = """[[#tag param="value" /]]"""
        result = parser.parse_bracket_sections(content.splitlines(), "<string>")
        sections = result["sections"]

        assert sections[0]["tags"] == ["#tag"]
        assert sections[0]["params"] == {"param": "value"}
        assert sections[0]["is_self_closing"] is True

    def test_self_closing_section_span_multilines(self, parser):
        """Test self-closing tag syntax"""
        content = """[[#tag param="value" /]]"""
        result = parser.parse_bracket_sections(content.splitlines(), "<string>")
        sections = result["sections"]

        assert sections[0]["tags"] == ["#tag"]
        assert sections[0]["params"] == {"param": "value"}
        assert sections[0]["is_self_closing"] is True

    def test_basic_content_preservation(self, parser):
        """Test basic content is preserved exactly as-is"""
        data = """[[#section]]
content
[[/]]

[[#section]]
space afterwards
[[/]]

[[#section]]
    space before
[[/]]

[[#section]]
\ttab before
[[/]]"""

        result = parser.parse_bracket_sections(data.splitlines(), "<string>")
        sections = result["sections"]
        assert sections[0]["raw_content"].rstrip("\n") == "content"
        assert sections[1]["raw_content"].rstrip("\n") == "space afterwards"
        assert sections[2]["raw_content"].rstrip("\n") == "    space before"
        assert sections[3]["raw_content"].rstrip("\n") == "\ttab before"

    def test_multiline_content(self, parser):
        """Test preservation of multiline content and blank lines"""
        content = """[[#section]]

pre and post blank lines

[[/]]"""
        result = parser.parse_bracket_sections(
            content.splitlines(keepends=True), "<string>"
        )
        sections = result["sections"]
        assert sections[0]["raw_content"] == "\npre and post blank lines\n"

    def test_nested_brackets_in_content(self, parser):
        """Test that bracket patterns inside content are preserved.

        Note: The new simplified parser treats [[#inner]] as content when
        it appears inside another section. The pattern [[/]] uniquely
        identifies section endings.
        """
        content = """[[#outer]]
Some content with [[#inner]] pattern preserved
[[/]]"""

        result = parser.parse_bracket_sections(content.splitlines(), "<string>")
        sections = result["sections"]
        assert len(sections) == 1
        assert "[[#inner]]" in sections[0]["raw_content"]

    def test_unclosed_section(self, parser):
        """Test unclosed section raises error"""
        content = "[[#unclosed]]\nsome content"
        with pytest.raises(FlexTagSyntaxError) as exc:
            parser.parse_bracket_sections(content.splitlines(), "<string>")
        assert "No matching close" in str(exc.value)

    def test_bare_close_tag_is_empty_section(self, parser):
        """Test that a bare [[/]] is treated as an empty self-closing section.

        With the new simplified syntax, [[/]] alone is valid and creates
        an empty section with no tags.
        """
        input_str = "[[/]]"
        result = parser.parse_bracket_sections(input_str.splitlines(), "<string>")
        sections = result["sections"]
        assert len(sections) == 1
        assert sections[0]["tags"] == []
        assert sections[0]["is_self_closing"] is True
        assert sections[0]["raw_content"] == ""

    def test_type_declaration(self, parser):
        """Test type declaration parsing"""
        content = """[[#section]]
raw content 1
[[/]]

[[#section]]: text
raw content 2
[[/]]

[[#section]]: yaml
key: value
[[/]]
"""
        result = parser.parse_bracket_sections(
            content.splitlines(keepends=True), "<string>"
        )
        sections = result["sections"]
        assert sections[0]["type_decl"] == ""
        assert sections[1]["type_decl"] == "text"
        assert sections[2]["type_decl"] == "yaml"

    def test_multiline_content_preservation(self, parser):
        """Test preservation of empty lines within content"""
        data = """[[#section]]

pre and post blank lines

[[/]]"""
        result = parser.parse_bracket_sections(
            data.splitlines(keepends=True), "<string>"
        )
        sections = result["sections"]
        assert sections[0]["raw_content"] == "\npre and post blank lines\n"

    def test_empty_content_variations(self, parser):
        """Test handling of empty and nearly-empty sections"""
        data = """[[#section]][[/]]

[[#section]]
[[/]]

[[#section]]


[[/]]"""

        result = parser.parse_bracket_sections(
            data.splitlines(keepends=True), "<string>"
        )
        sections = result["sections"]
        assert sections[0]["raw_content"] == ""  # No newline
        assert sections[1]["raw_content"] == ""  # Single newline gets stripped
        assert sections[2]["raw_content"] == "\n"  # Internal newline preserved

    def test_empty_content_variations_from_load(self):
        """Test handling of empty and nearly-empty sections"""
        data = """[[#section]][[/]]

[[#section]]
[[/]]

[[#section]]


[[/]]"""
        view = FlexTag.load(string=data)
        # Case 1: No space between header and footer
        assert view.sections[0].content == ""  # No newline
        # Case 2: Single newline between header and footer
        assert view.sections[1].content == ""  # Single newline gets stripped
        # Case 3: Multiple blank lines
        assert view.sections[2].raw_content == "\n"  # One internal newline preserved

    def test_yaml_content_parsing(self, parser):
        """Test YAML content type recognition"""
        content = """[[#config]]: yaml
debug: true
items:
  - "apple"
  - "banana"
[[/]]"""

        result = parser.parse_bracket_sections(content.splitlines(), "<string>")
        sections = result["sections"]
        assert sections[0]["type_decl"] == "yaml"
        assert "debug: true" in sections[0]["raw_content"]

    def test_text_with_yaml_like_content(self, parser):
        """Test that YAML-like content in text sections stays unparsed"""
        content = """[[#section]]: text
key: value
- list item
[[/]]"""

        result = parser.parse_bracket_sections(content.splitlines(), "<string>")
        sections = result["sections"]
        assert sections[0]["type_decl"] == "text"
        assert "key: value" in sections[0]["raw_content"]

    def test_meta_block_parsing(self, parser):
        """Test parsing of ---meta--- block"""
        content = """---meta---
[[#plugin @plugins.chart version=1.0]]
---/meta---

[[#content]]
Content here
[[/]]"""

        result = parser.parse_bracket_sections(content.splitlines(), "<string>")
        assert result["meta_content"] is not None
        assert "#plugin" in result["meta_content"]
        assert "@plugins.chart" in result["meta_content"]

    def test_schema_block_parsing(self, parser):
        """Test parsing of ---schema--- block"""
        content = """---schema---
[[#notes #draft]]+: text
[[#config]]: yaml
---/schema---

[[#notes #draft]]
A draft note
[[/]]"""

        result = parser.parse_bracket_sections(content.splitlines(), "<string>")
        assert result["schema_content"] is not None
        assert "[[#notes #draft]]+: text" in result["schema_content"]

    def test_quoted_parameter_values(self, parser):
        """Test handling of quoted parameter values"""
        content = """[[#section param="value with spaces" other='single quotes']]
content
[[/]]"""

        result = parser.parse_bracket_sections(content.splitlines(), "<string>")
        sections = result["sections"]
        assert sections[0]["params"] == {
            "param": "value with spaces",
            "other": "single quotes",
        }

    def test_multiple_type_declarations_error(self, parser):
        content = """[[#section]]: ftml: text
    content
    [[/]]"""

        with pytest.raises(FlexTagSyntaxError) as excinfo:
            parser.parse_bracket_sections(content.splitlines(), "<string>")

        error_msg = str(excinfo.value)
        assert "Multiple type declarations" in error_msg
        # Also check that the location information is present
        assert "<string> L1" in error_msg  # Check line number
        assert "^" in error_msg  # Check visual pointer is present
