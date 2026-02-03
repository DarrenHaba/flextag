import os
import tempfile
import unittest

from flextag import FlexTag, SchemaSectionError, SchemaTypeError

try:
    import ftml

    HAS_FTML = True
except ImportError:
    HAS_FTML = False

requires_ftml = unittest.skipUnless(HAS_FTML, "ftml package not installed")


class TestFlexTagBasics(unittest.TestCase):
    """Basic FlexTag functionality tests."""

    def test_empty_section(self):
        """Test an empty section."""
        data = "[[test /]]"
        view = FlexTag.load(string=data, validate=False)
        self.assertEqual(len(view.sections), 1)
        section = view.sections[0]
        self.assertEqual(section.id, "test")
        self.assertEqual(section.raw_content, "")
        self.assertEqual(section.content, "")
        self.assertTrue(section.is_self_closing)

    def test_raw_content(self):
        """Test raw content handling."""
        data = """
        [[test]]
        This is raw content
        that spans multiple lines
        [[/test]]
        """
        view = FlexTag.load(string=data, validate=False)
        self.assertEqual(len(view.sections), 1)
        section = view.sections[0]
        self.assertEqual(section.id, "test")
        self.assertEqual(section.type_name, "text")  # Default type is text
        self.assertIn("This is raw content", section.content)
        self.assertIn("that spans multiple lines", section.content)

    def test_explicit_text_content(self):
        """Test explicit text content type."""
        data = """
        [[test]]: text
        This is explicit text content
        [[/test]]
        """
        view = FlexTag.load(string=data, validate=False)
        section = view.sections[0]
        self.assertEqual(section.type_name, "text")
        self.assertIn("This is explicit text content", section.content)

    @requires_ftml
    def test_ftml_content(self):
        """Test FTML content parsing."""
        data = """
        [[config]]: ftml
        model_name = "GPT-4"
        max_tokens = 8192
        temperature = 0.7
        [[/config]]
        """
        view = FlexTag.load(string=data, validate=False)
        section = view.sections[0]
        self.assertEqual(section.type_name, "ftml")
        self.assertEqual(section.content["model_name"], "GPT-4")
        self.assertEqual(section.content["max_tokens"], 8192)
        self.assertEqual(section.content["temperature"], 0.7)


class TestFlexTagMetadata(unittest.TestCase):
    """Tests for tags, paths, and parameters."""

    def test_tags(self):
        """Test tag handling."""
        data = """
        [[test #draft #important]]
        Content
        [[/test]]
        """
        view = FlexTag.load(string=data, validate=False)
        section = view.sections[0]
        self.assertEqual(section.id, "test")
        self.assertIn("#draft", section.tags)
        self.assertIn("#important", section.tags)

    def test_at_prefix_paths(self):
        """Test @ prefix for paths."""
        data = """
        [[test @category.subcategory @topic]]
        Content
        [[/test]]
        """
        view = FlexTag.load(string=data, validate=False)
        section = view.sections[0]
        self.assertEqual(section.id, "test")
        self.assertIn("@category.subcategory", section.paths)
        self.assertIn("@topic", section.paths)

    def test_parameters(self):
        """Test parameter handling."""
        data = """
        [[test str_param="value" int_param=42 float_param=3.14 bool_param=true null_param=null]]
        Content
        [[/test]]
        """
        view = FlexTag.load(string=data, validate=False)
        section = view.sections[0]
        self.assertEqual(section.parameters["str_param"], "value")
        self.assertEqual(section.parameters["int_param"], 42)
        self.assertEqual(section.parameters["float_param"], 3.14)
        self.assertEqual(section.parameters["bool_param"], True)
        self.assertIsNone(section.parameters["null_param"])


class TestFlexTagSchema(unittest.TestCase):
    """Tests for schema validation."""

    def test_traditional_schema_validation_success(self):
        """Test traditional schema validation (success case)."""
        data = """
        [[]]: schema
        [notes #draft]+: text
        [[/]]

        [[notes #draft]]
        This is a draft note
        [[/notes]]

        """
        view = FlexTag.load(string=data, validate=True)
        self.assertEqual(len(view.sections), 1)
        self.assertEqual(view.sections[0].id, "notes")
        self.assertIn("#draft", view.sections[0].tags)

    def test_traditional_schema_validation_failure(self):
        """Test traditional schema validation (failure case)."""
        data = """
        [[]]: schema
        [notes #draft]+: text
        [[/]]

        [[notes]]
        This note is missing the required #draft tag
        [[/notes]]
        """
        with self.assertRaises(SchemaSectionError):
            FlexTag.load(string=data, validate=True)

    def test_traditional_schema_type_validation(self):
        """Test schema content type validation."""
        data = """
        [[]]: schema
        [config]: ftml
        [[/]]

        [[config]]: text
        Should be FTML content
        [[/config]]
        """
        with self.assertRaises(SchemaTypeError):
            FlexTag.load(string=data, validate=True)

    @requires_ftml
    def test_ftml_schema_syntax(self):
        """Test FTML schema syntax recognition."""
        data = """
        [[]]: schema
        [config]: ftml
        // FTML Schema
        model_name: str
        max_tokens: int
        [/]
        [[/]]

        [[config]]: ftml
        model_name = "GPT-4"
        max_tokens = 8192
        [[/config]]
        """
        # This should pass without error
        view = FlexTag.load(string=data, validate=True)
        self.assertEqual(len(view.sections), 1)
        self.assertEqual(view.sections[0].id, "config")
        self.assertEqual(view.sections[0].content["model_name"], "GPT-4")


class TestFlexTagFile(unittest.TestCase):
    """Tests for file loading and saving."""

    def test_load_from_file(self):
        """Test loading from a file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ft", delete=False) as f:
            f.write(
                """
            [[test]]
            Content from file
            [[/test]]
            """
            )
            filepath = f.name

        try:
            view = FlexTag.load(path=filepath, validate=False)
            self.assertEqual(len(view.sections), 1)
            self.assertEqual(view.sections[0].id, "test")
            self.assertIn("Content from file", view.sections[0].content)
        finally:
            os.unlink(filepath)

    def test_load_multiple_files(self):
        """Test loading from multiple files."""
        filepaths = []
        file_contents = [
            """[[one]]
            First file
            [[/one]]""",
            """[[two]]
            Second file
            [[/two]]""",
        ]

        try:
            for content in file_contents:
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".ft", delete=False
                ) as f:
                    f.write(content)
                    filepaths.append(f.name)

            view = FlexTag.load(path=filepaths, validate=False)
            self.assertEqual(len(view.sections), 2)
            ids = [s.id for s in view.sections]
            self.assertIn("one", ids)
            self.assertIn("two", ids)
        finally:
            for filepath in filepaths:
                os.unlink(filepath)


class TestFlexTagFilter(unittest.TestCase):
    """Tests for filtering."""

    def test_filter_by_tag(self):
        """Test filtering by tag."""
        data = """
        [[one #draft]]
        Draft content
        [[/one]]

        [[two #final]]
        Final content
        [[/two]]
        """
        view = FlexTag.load(string=data, validate=False)
        filtered = view.filter("#draft")
        self.assertEqual(len(filtered.sections), 1)
        self.assertEqual(filtered.sections[0].id, "one")

    def test_complex_filter(self):
        """Test complex filtering."""
        data = """
        [[one #draft @research]]
        Draft research
        [[/one]]

        [[two #draft @development]]
        Draft development
        [[/two]]

        [[three #final @research]]
        Final research
        [[/three]]
        """
        view = FlexTag.load(string=data, validate=False)

        # Filter by tag AND path
        filtered = view.filter("#draft @research")
        self.assertEqual(len(filtered.sections), 1)
        self.assertEqual(filtered.sections[0].id, "one")

        # Filter by tag OR path
        filtered = view.filter("#final OR @development")
        self.assertEqual(len(filtered.sections), 2)
        ids = [s.id for s in filtered.sections]
        self.assertIn("two", ids)
        self.assertIn("three", ids)


if __name__ == "__main__":
    unittest.main()
