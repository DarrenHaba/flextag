import pytest

from flextag.flextag import FlexParser, FlexTagSyntaxError, FlexTag


class TestFlexParser:
    """Test the basic parsing functionality"""

    @pytest.fixture
    def parser(self):
        return FlexParser()

    def test_basic_section_parsing(self, parser):
        """Test parsing a simple section with just an ID"""
        content = """[[simple]]
        Basic content
        [[/simple]]"""

        sections = parser.parse_bracket_sections(content.splitlines(), "<string>")
        assert len(sections) == 1
        assert sections[0]["section_id"] == "simple"
        assert "Basic content" in sections[0]["raw_content"]

    def test_basic_section_parsing_prams(self, parser):
        """Test basic section parsing with metadata"""
        content = """[[#tag1 #tag2 key="value"]]
    content
    [[/]]"""

        sections = parser.parse_bracket_sections(content.splitlines(), "<string>")
        assert len(sections) == 1
        section = sections[0]

        assert sorted(section["tags"]) == sorted(["#tag1", "#tag2"])
        print(section["params"])
        assert section["params"] == {"key": "value"}
        assert "content" in section["raw_content"]

    def test_section_with_metadata(self, parser):
        """Test parsing a section with tags, paths, and params"""
        content = """[[doc #draft @path key=value]]
        Content
        [[/doc]]"""

        sections = parser.parse_bracket_sections(content.splitlines(), "<string>")
        assert sections[0]["tags"] == ["#draft"]
        assert sections[0]["paths"] == ["@path"]
        assert sections[0]["params"] == {"key": "value"}

    def test_section_with_comment(self, parser):
        """Test parsing a section with tags, paths, and params"""
        content = """
        # This is a valid comment.
        [[]]
        Content
        [[/]]"""

        sections = parser.parse_bracket_sections(content.splitlines(), "<string>")
        assert len(sections) == 1
        assert "Content" in sections[0]["raw_content"]

    def test_section_with_invalid_comment(self, parser):
        """Test that non-comment lines between sections raise FlexTagSyntaxError"""
        content = """
        This is an invalid comment
        [[]]
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
        sections = parser.parse_bracket_sections(content.splitlines(), "<string>")
        assert sections[0]["raw_content"] == ""

    def test_self_closing_section(self, parser):
        """Test self-closing tag syntax"""
        content = """[[#tag param="value" /]]"""
        sections = parser.parse_bracket_sections(content.splitlines(), "<string>")

        assert sections[0]["tags"] == ["#tag"]
        assert sections[0]["params"] == {"param": "value"}
        assert sections[0]["is_self_closing"] is True

    def test_self_closing_section_span_multilines(self, parser):
        """Test self-closing tag syntax"""
        content = """[[#tag param="value" /]]"""
        sections = parser.parse_bracket_sections(content.splitlines(), "<string>")

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

        sections = parser.parse_bracket_sections(data.splitlines(), "<string>")
        assert sections[0]["raw_content"].rstrip("\n") == "content"
        assert sections[1]["raw_content"].rstrip("\n") == "space afterwards    "
        assert sections[2]["raw_content"].rstrip("\n") == "    space before"
        assert sections[3]["raw_content"].rstrip("\n") == "\ttab before"

    def test_multiline_content(self, parser):
        """Test preservation of multiline content and blank lines"""
        content = """[[#section]]

pre and post blank lines

[[/]]"""
        sections = parser.parse_bracket_sections(
            content.splitlines(keepends=True), "<string>"
        )
        assert sections[0]["raw_content"] == "\npre and post blank lines\n"

    def test_invalid_nesting(self, parser):
        """Test that nested sections raise an error"""
        content = """[[outer]]
        [[inner]]
        Content
        [[/inner]]
        [[/outer]]"""

        with pytest.raises(FlexTagSyntaxError):
            parser.parse_bracket_sections(content.splitlines(), "<string>")

    @pytest.mark.parametrize(
        "input_str,expected_error",
        [
            # Case 1: Truly unclosed section (no close tag at all)
            (
                "[[unclosed]]\nsome content",
                "[<string> L2] No matching close for ID='unclosed'",
            ),
            # Case 2: Mismatched close tag ID
            (
                "[[a]]\ncontent\n[[/b]]",
                "[<string> L3] Mismatched close ID='b', expected='a'",
            ),
            # Case 3: Multiple sections with second unclosed
            (
                "[[a]]\ncontent\n[[/a]]\n[[b]]\nmore content",
                "[<string> L5] No matching close for ID='b'",
            ),
            # Case 4: Empty file with just a close tag
            (
                "[[/unopened]]",
                "[<string> L1] No matching close for ID='/unopened'",  # Note: parser includes the '/' in ID
            ),
        ],
    )
    def test_syntax_errors(self, parser, input_str, expected_error):
        """Test various syntax error conditions with exact error messages"""
        with pytest.raises(FlexTagSyntaxError) as exc:
            parser.parse_bracket_sections(input_str.splitlines(), "<string>")
        assert str(exc.value) == expected_error

    def test_unopened_section(self, parser):
        """Test specific case of unopened section"""
        input_str = "[[/unopened]]"
        # This might need adjustment based on how your parser actually handles this case
        with pytest.raises(FlexTagSyntaxError) as exc:
            parser.parse_bracket_sections(input_str.splitlines(), "<string>")
        # You might want to check for specific error attributes rather than message
        assert "Mismatched" in str(exc.value) or "No matching" in str(exc.value)

    def test_type_declaration(self, parser):
        """Test type declaration parsing"""
        content = """[[section]]
raw content 1
[[/section]]

[[section]]: raw
raw content 2
[[/section]]

[[section]]: yaml
key: value
[[/section]]
"""
        sections = parser.parse_bracket_sections(
            content.splitlines(keepends=True), "<string>"
        )
        assert sections[0]["type_decl"] == ""
        assert sections[1]["type_decl"] == "raw"
        assert sections[2]["type_decl"] == "yaml"

    def test_multiline_content_preservation(self, parser):
        """Test preservation of empty lines within content"""
        data = """[[#section]]

pre and post blank lines

[[/]]"""
        sections = parser.parse_bracket_sections(
            data.splitlines(keepends=True), "<string>"
        )
        assert sections[0]["raw_content"] == "\npre and post blank lines\n"

    def test_empty_content_variations(self, parser):
        """Test handling of empty and nearly-empty sections"""
        data = """[[#section]][[/]]

[[#section]]
[[/]]

[[#section]]
 
[[/]]

[[#section]]


[[/]]"""

        sections = parser.parse_bracket_sections(
            data.splitlines(keepends=True), "<string>"
        )
        assert sections[0]["raw_content"] == ""  # No newline
        assert sections[1]["raw_content"] == ""  # Single newline gets stripped
        assert sections[2]["raw_content"] == " "  # Space preserved
        assert sections[3]["raw_content"] == "\n"  # Internal newline preserved

    def test_empty_content_variations_from_load(self):
        """Test handling of empty and nearly-empty sections"""
        data = """[[#section]][[/]]

[[#section]]
[[/]]

[[#section]]
 
[[/]]

[[#section]]


[[/]]"""
        view = FlexTag.load(string=data)
        # Case 1: No space between header and footer
        assert view.sections[0].content == ""  # No newline
        # Case 2: Single newline between header and footer
        assert view.sections[1].content == ""  # Single newline gets stripped
        # Case 3: Space and newline
        assert view.sections[2].content == " "  # Space preserved
        # Case 4: Multiple blank lines
        assert view.sections[3].raw_content == "\n"  # One internal newline preserved

    def test_content_type_inheritance(self, parser):
        """Test that content type is properly inherited from defaults"""
        content = """[[]]: defaults
[type="yaml"]
[[/]]

[[section]]
key: value
[[/section]]"""

        sections = parser.parse_bracket_sections(
            content.splitlines(keepends=True), "<string>"
        )
        assert sections[1]["type_decl"] == ""  # No explicit type
        # Note: actual type inheritance is handled at Container level

    def test_yaml_content_parsing(self, parser):
        """Test YAML content type recognition"""
        content = """[[config]]: yaml
debug: true
items:
  - "apple"
  - "banana"
[[/config]]"""

        sections = parser.parse_bracket_sections(content.splitlines(), "<string>")
        assert sections[0]["type_decl"] == "yaml"
        assert "debug: true" in sections[0]["raw_content"]

    def test_text_with_yaml_like_content(self, parser):
        """Test that YAML-like content in text sections stays unparsed"""
        content = """[[section]]: text
key: value
- list item
[[/section]]"""

        sections = parser.parse_bracket_sections(content.splitlines(), "<string>")
        assert sections[0]["type_decl"] == "text"
        assert "key: value" in sections[0]["raw_content"]

    def test_container_section_parsing(self, parser):
        """Test parsing of container metadata section"""
        content = """[[]]: container
[my_container #tag version=1.0]
[[/]]"""

        sections = parser.parse_bracket_sections(content.splitlines(), "<string>")
        assert sections[0]["type_decl"] == "container"
        assert "[my_container #tag version=1.0]" in sections[0]["raw_content"]

    def test_schema_section_parsing(self, parser):
        """Test parsing of schema section with new format"""
        content = """[[]]: schema
[notes #draft /]?: text
[config #settings]: yaml
[[/]]"""

        sections = parser.parse_bracket_sections(content.splitlines(), "<string>")
        assert sections[0]["type_decl"] == "schema"
        assert "[notes #draft /]?: text" in sections[0]["raw_content"]

    def test_quoted_parameter_values(self, parser):
        """Test handling of quoted parameter values"""
        content = """[[section param="value with spaces" other='single quotes']]
content
[[/section]]"""

        sections = parser.parse_bracket_sections(content.splitlines(), "<string>")
        assert sections[0]["params"] == {
            "param": "value with spaces",
            "other": "single quotes",
        }

    def test_multiple_type_declarations_error(self, parser):
        content = """[[section]]: ftml: text
    content
    [[/section]]"""

        with pytest.raises(FlexTagSyntaxError) as excinfo:
            parser.parse_bracket_sections(content.splitlines(), "<string>")

        error_msg = str(excinfo.value)
        assert "Multiple type declarations" in error_msg
        # Also check that the location information is present
        assert "<string> L1" in error_msg  # Check line number
        assert "^" in error_msg  # Check visual pointer is present
