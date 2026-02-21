"""
Test suite for FlexTag text and binary content types.

FlexTag supports two basic (non-markup) content types:
- text: Returns content as a Python str (default)
- binary: Returns content as bytes

Markup types (json, yaml, toml, ftml) are tested elsewhere.
"""

import os
import tempfile

import flextag
from flextag.flextag import FlexTag, Section

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_section(content_lines, type_name="text", tag="#test"):
    """Create a Section directly from content lines and a type name."""
    open_line_text = f"[[{tag}]]: {type_name}\n"
    close_line_text = "[[/]]\n"
    all_lines = (
        [open_line_text] + [line + "\n" for line in content_lines] + [close_line_text]
    )

    return Section(
        section_id="",
        tags=[tag],
        parameters={},
        type_name=type_name,
        open_line=0,
        close_line=len(all_lines) - 1,
        is_self_closing=False,
        all_lines=all_lines,
        source_path="<test>",
    )


def write_binary_file(raw_bytes: bytes) -> str:
    """Write raw bytes to a temp .ft file and return the path."""
    tmp = tempfile.NamedTemporaryFile(
        mode="wb", suffix=".ft", delete=False, dir=tempfile.gettempdir()
    )
    tmp.write(raw_bytes)
    tmp.close()
    return tmp.name


# ===========================================================================
# TEXT TYPE
# ===========================================================================


class TestTextType:
    """Sections with type 'text' (or no type) return content as str."""

    def test_text_type_returns_string(self):
        """Type 'text' returns content as a Python str."""
        test_string = """
[[#doc]]: text
Hello, world!
[[/]]
"""
        view = flextag.load(string=test_string)
        content = view.sections[0].content
        assert isinstance(content, str)
        assert content == "Hello, world!"

    def test_text_preserves_unicode(self):
        """Text content with Unicode characters is preserved."""
        test_string = """
[[#unicode_doc]]: text
Héllo wörld! 你好世界 🌍🚀
[[/]]
"""
        view = flextag.load(string=test_string)
        content = view.sections[0].content
        assert "Héllo wörld!" in content
        assert "你好世界" in content
        assert "🌍🚀" in content

    def test_text_multiline_preserved(self):
        """Multi-line text content preserves all lines."""
        test_string = """
[[#multiline]]: text
Line 1
Line 2
Line 3
[[/]]
"""
        view = flextag.load(string=test_string)
        content = view.sections[0].content
        assert content == "Line 1\nLine 2\nLine 3"

    def test_default_type_is_text(self):
        """Sections with no explicit type default to 'text'."""
        test_string = """
[[#no_type]]
Default type content
[[/]]
"""
        view = flextag.load(string=test_string)
        section = view.sections[0]
        assert section.type_name == "text"
        assert isinstance(section.content, str)
        assert section.content == "Default type content"

    def test_text_case_insensitive(self):
        """Type matching is case-insensitive."""
        for type_name in ("TEXT", "Text", "text", "tExT"):
            section = make_section(["Case test"], type_name=type_name)
            assert section.content == "Case test"

    def test_empty_text_section(self):
        """An empty text section returns empty string."""
        test_string = """
[[#empty]]: text
[[/]]
"""
        view = flextag.load(string=test_string)
        assert view.sections[0].content == ""


# ===========================================================================
# BINARY TYPE
# ===========================================================================


class TestBinaryType:
    """Sections with type 'binary' return content as bytes."""

    def test_binary_returns_bytes(self):
        """Type 'binary' returns content as bytes."""
        test_string = """
[[#data]]: binary
Hello binary
[[/]]
"""
        view = flextag.load(string=test_string)
        content = view.sections[0].content
        assert isinstance(content, bytes)
        assert content == b"Hello binary"

    def test_binary_preserves_ascii(self):
        """Binary mode correctly converts ASCII text to bytes."""
        section = make_section(["Line 1", "Line 2"], type_name="binary")
        content = section.content
        assert isinstance(content, bytes)
        assert content == b"Line 1\nLine 2"

    def test_binary_preserves_utf8_multibyte(self):
        """Binary mode preserves multi-byte UTF-8 sequences."""
        section = make_section(["café"], type_name="binary")
        content = section.content
        assert isinstance(content, bytes)
        assert content == "café".encode()

    def test_binary_roundtrip_non_utf8_bytes(self):
        """Non-UTF-8 bytes survive the round-trip through surrogateescape.

        This is the critical test for binary support. Bytes that are not
        valid UTF-8 must be preserved exactly.
        """
        # Latin-1 bytes 0x80-0xFF are not valid standalone UTF-8
        test_bytes = bytes(range(0x80, 0x100))

        file_content = b"[[#data]]: binary\n" + test_bytes + b"\n[[/]]\n"
        filepath = write_binary_file(file_content)
        try:
            view = FlexTag.load(path=filepath, validate=False)
            content = view.sections[0].content
            assert isinstance(content, bytes)
            assert content == test_bytes
        finally:
            os.unlink(filepath)

    def test_binary_single_non_utf8_byte(self):
        """A single non-UTF-8 byte (0xFF) survives the binary round-trip."""
        file_content = b"[[#data]]: binary\n\xff\n[[/]]\n"
        filepath = write_binary_file(file_content)
        try:
            view = FlexTag.load(path=filepath, validate=False)
            content = view.sections[0].content
            assert isinstance(content, bytes)
            assert content == b"\xff"
        finally:
            os.unlink(filepath)

    def test_binary_all_byte_values(self):
        """Every byte value (except newlines) survives binary round-trip.

        We exclude 0x0A and 0x0D because text-mode parsing handles newlines.
        """
        test_bytes = bytes([b for b in range(256) if b not in (0x0A, 0x0D)])

        file_content = b"[[#data]]: binary\n" + test_bytes + b"\n[[/]]\n"
        filepath = write_binary_file(file_content)
        try:
            view = FlexTag.load(path=filepath, validate=False)
            content = view.sections[0].content
            assert content == test_bytes
        finally:
            os.unlink(filepath)

    def test_empty_binary_section(self):
        """An empty binary section returns empty string (early return)."""
        test_string = """
[[#empty]]: binary
[[/]]
"""
        view = flextag.load(string=test_string)
        assert view.sections[0].content == ""


# ===========================================================================
# MIXED SECTIONS
# ===========================================================================


class TestMixedSections:
    """Different sections can have different types in the same file."""

    def test_text_and_binary_together(self):
        """A file can have both text and binary sections."""
        test_string = """
[[#text_part]]: text
Hello, this is text.
[[/]]

[[#binary_part]]: binary
Raw binary data here
[[/]]
"""
        view = flextag.load(string=test_string)
        text_content = view.sections[0].content
        binary_content = view.sections[1].content

        assert isinstance(text_content, str)
        assert text_content == "Hello, this is text."
        assert isinstance(binary_content, bytes)
        assert binary_content == b"Raw binary data here"

    def test_text_binary_and_markup_together(self):
        """Text and binary sections coexist with markup sections."""
        test_string = """
[[#text]]: text
Plain text content
[[/]]

[[#config]]: json
{"key": "value"}
[[/]]

[[#data]]: binary
Binary stuff
[[/]]

[[#meta]]: yaml
name: test
version: 1
[[/]]
"""
        view = flextag.load(string=test_string)
        sections = view.sections

        assert len(sections) == 4

        # Text
        assert isinstance(sections[0].content, str)
        assert sections[0].content == "Plain text content"

        # JSON
        assert isinstance(sections[1].content, dict)
        assert sections[1].content["key"] == "value"

        # Binary
        assert isinstance(sections[2].content, bytes)
        assert sections[2].content == b"Binary stuff"

        # YAML
        assert isinstance(sections[3].content, dict)
        assert sections[3].content["name"] == "test"


# ===========================================================================
# EDGE CASES
# ===========================================================================


class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_content_caching(self):
        """The content property caches its result."""
        section = make_section(["Cached content"], type_name="text")
        first_access = section.content
        second_access = section.content
        assert first_access is second_access

    def test_unknown_type_returns_text_with_warning(self, caplog):
        """An unknown type name returns text with a warning."""
        import logging

        test_string = """
[[#data]]: some_unknown_type
Content here
[[/]]
"""
        with caplog.at_level(logging.WARNING):
            view = flextag.load(string=test_string)
            content = view.sections[0].content

        assert isinstance(content, str)
        assert content == "Content here"
        assert any("unknown" in r.message.lower() for r in caplog.records)

    def test_self_closing_section(self):
        """A self-closing section returns empty string."""
        test_string = """
[[#self_close /]]: text
"""
        view = flextag.load(string=test_string)
        assert view.sections[0].content == ""

    def test_whitespace_only_content(self):
        """Sections with only whitespace preserve it."""
        section = make_section(["   "], type_name="text")
        assert section.content == "   "
