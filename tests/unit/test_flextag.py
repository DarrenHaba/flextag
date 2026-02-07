import os
import tempfile
import unittest

from flextag import FlexTag

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
        data = "[[#test /]]"
        view = FlexTag.load(string=data, validate=False)
        self.assertEqual(len(view.sections), 1)
        section = view.sections[0]
        self.assertIn("#test", section.tags)
        self.assertEqual(section.raw_content, "")
        self.assertEqual(section.content, "")
        self.assertTrue(section.is_self_closing)

    def test_raw_content(self):
        """Test raw content handling."""
        data = """
        [[#test]]
        This is raw content
        that spans multiple lines
        [[/]]
        """
        view = FlexTag.load(string=data, validate=False)
        self.assertEqual(len(view.sections), 1)
        section = view.sections[0]
        self.assertIn("#test", section.tags)
        self.assertEqual(section.type_name, "text")  # Default type is text
        self.assertIn("This is raw content", section.content)
        self.assertIn("that spans multiple lines", section.content)

    def test_explicit_text_content(self):
        """Test explicit text content type."""
        data = """
        [[#test]]: text
        This is explicit text content
        [[/]]
        """
        view = FlexTag.load(string=data, validate=False)
        section = view.sections[0]
        self.assertEqual(section.type_name, "text")
        self.assertIn("This is explicit text content", section.content)

    @requires_ftml
    def test_ftml_content(self):
        """Test FTML content parsing."""
        data = """
        [[#config]]: ftml
        model_name = "GPT-4"
        max_tokens = 8192
        temperature = 0.7
        [[/]]
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
        [[#test #draft #important]]
        Content
        [[/]]
        """
        view = FlexTag.load(string=data, validate=False)
        section = view.sections[0]
        self.assertIn("#test", section.tags)
        self.assertIn("#draft", section.tags)
        self.assertIn("#important", section.tags)

    def test_hierarchical_tags(self):
        """Test hierarchical tags with dot notation."""
        data = """
        [[#test #category.subcategory #topic]]
        Content
        [[/]]
        """
        view = FlexTag.load(string=data, validate=False)
        section = view.sections[0]
        self.assertIn("#test", section.tags)
        self.assertIn("#category.subcategory", section.tags)
        self.assertIn("#topic", section.tags)

    def test_parameters(self):
        """Test parameter handling."""
        data = """
        [[#test str_param="value" int_param=42 float_param=3.14 bool_param=true null_param=null]]
        Content
        [[/]]
        """
        view = FlexTag.load(string=data, validate=False)
        section = view.sections[0]
        self.assertEqual(section.parameters["str_param"], "value")
        self.assertEqual(section.parameters["int_param"], 42)
        self.assertEqual(section.parameters["float_param"], 3.14)
        self.assertEqual(section.parameters["bool_param"], True)
        self.assertIsNone(section.parameters["null_param"])


class TestFlexTagSchema(unittest.TestCase):
    """Tests for schema validation using ftml-schema sections."""

    def test_basic_schema_validation_success(self):
        """Test basic schema validation with matching properties."""
        data = """
[[#schema.product]]: ftml-schema
name: str
price: float
[[/]]

[[#schema.product name="Widget" price=9.99]]: text
Product description here
[[/]]
        """
        view = FlexTag.load(string=data, validate=True)
        # Schema section + data section, but only data section in .sections
        data_sections = [s for s in view.sections if s.type_name != "ftml-schema"]
        self.assertEqual(len(data_sections), 1)
        self.assertEqual(data_sections[0].parameters["name"], "Widget")
        self.assertEqual(data_sections[0].parameters["price"], 9.99)

    def test_descendant_match_with_star(self):
        """Test that #tag* in schema matches descendant tags."""
        data = """
[[#schema.product*]]: ftml-schema
name: str
[[/]]

[[#schema.product.laptop name="ThinkPad"]]: text
Laptop matches because schema uses * for descendants
[[/]]
        """
        view = FlexTag.load(string=data, validate=True)
        data_sections = [s for s in view.sections if s.type_name != "ftml-schema"]
        self.assertEqual(len(data_sections), 1)
        self.assertIn("#schema.product.laptop", data_sections[0].tags)

    def test_exact_match_does_not_match_descendants(self):
        """Test that #tag (no modifier) does NOT match descendant tags."""
        data = """
[[#schema.product]]: ftml-schema
name: str
[[/]]

[[#schema.product.laptop name="ThinkPad"]]: text
Should NOT be validated — schema is exact match only
[[/]]

[[#schema.product.laptop]]: text
Missing name — but no schema applies so this is fine
[[/]]
        """
        # Should not raise — the schema only matches exact #schema.product,
        # not #schema.product.laptop
        view = FlexTag.load(string=data, validate=True)
        data_sections = [s for s in view.sections if s.type_name != "ftml-schema"]
        self.assertEqual(len(data_sections), 2)

    def test_immediate_children_with_plus(self):
        """Test that #tag+ matches immediate children only."""
        data = """
[[#adapter+]]: ftml-schema
name: str
[[/]]

[[#adapter.live name="Binance"]]: text
One level deep — matches
[[/]]

[[#adapter.live.binance name="Deep"]]: text
Two levels deep — should NOT match the + schema
[[/]]

[[#adapter.live.binance]]: text
Two levels deep, no name — fine because schema doesn't apply
[[/]]
        """
        view = FlexTag.load(string=data, validate=True)
        data_sections = [s for s in view.sections if s.type_name != "ftml-schema"]
        self.assertEqual(len(data_sections), 3)

    def test_negation_with_bang(self):
        """Test that !#tag excludes sections with that tag from schema matching."""
        data = """
[[#adapter !#deprecated]]: ftml-schema
name: str
[[/]]

[[#adapter name="Active Adapter"]]: text
Has #adapter, no #deprecated — schema applies, valid
[[/]]

[[#adapter #deprecated name="Old Adapter"]]: text
Has #adapter AND #deprecated — schema does NOT apply
[[/]]

[[#adapter #deprecated]]: text
Has #adapter AND #deprecated — no schema, missing name is fine
[[/]]
        """
        view = FlexTag.load(string=data, validate=True)
        data_sections = [s for s in view.sections if s.type_name != "ftml-schema"]
        self.assertEqual(len(data_sections), 3)

    def test_unmatched_sections_allowed(self):
        """Test that sections without matching schemas are allowed."""
        data = """
[[#schema.product]]: ftml-schema
name: str
[[/]]

[[#other anything="allowed"]]: text
No schema matches this
[[/]]
        """
        view = FlexTag.load(string=data, validate=True)
        data_sections = [s for s in view.sections if s.type_name != "ftml-schema"]
        self.assertEqual(len(data_sections), 1)
        self.assertEqual(data_sections[0].parameters["anything"], "allowed")


class TestFlexTagFile(unittest.TestCase):
    """Tests for file loading and saving."""

    def test_load_from_file(self):
        """Test loading from a file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ft", delete=False) as f:
            f.write(
                """
            [[#test]]
            Content from file
            [[/]]
            """
            )
            filepath = f.name

        try:
            view = FlexTag.load(path=filepath, validate=False)
            self.assertEqual(len(view.sections), 1)
            self.assertIn("#test", view.sections[0].tags)
            self.assertIn("Content from file", view.sections[0].content)
        finally:
            os.unlink(filepath)

    def test_load_multiple_files(self):
        """Test loading from multiple files."""
        filepaths = []
        file_contents = [
            """[[#one]]
            First file
            [[/]]""",
            """[[#two]]
            Second file
            [[/]]""",
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
            all_tags = []
            for s in view.sections:
                all_tags.extend(s.tags)
            self.assertIn("#one", all_tags)
            self.assertIn("#two", all_tags)
        finally:
            for filepath in filepaths:
                os.unlink(filepath)


class TestFlexTagFilter(unittest.TestCase):
    """Tests for filtering."""

    def test_filter_by_tag(self):
        """Test filtering by tag."""
        data = """
        [[#one #draft]]
        Draft content
        [[/]]

        [[#two #final]]
        Final content
        [[/]]
        """
        view = FlexTag.load(string=data, validate=False)
        filtered = view.filter("#draft")
        self.assertEqual(len(filtered.sections), 1)
        self.assertIn("#one", filtered.sections[0].tags)

    def test_complex_filter(self):
        """Test complex filtering."""
        data = """
        [[#one #draft @research]]
        Draft research
        [[/]]

        [[#two #draft @development]]
        Draft development
        [[/]]

        [[#three #final @research]]
        Final research
        [[/]]
        """
        view = FlexTag.load(string=data, validate=False)

        # Filter by tag AND path
        filtered = view.filter("#draft @research")
        self.assertEqual(len(filtered.sections), 1)
        self.assertIn("#one", filtered.sections[0].tags)

        # Filter by tag OR path
        filtered = view.filter("#final OR @development")
        self.assertEqual(len(filtered.sections), 2)
        all_tags = []
        for s in filtered.sections:
            all_tags.extend(s.tags)
        self.assertIn("#two", all_tags)
        self.assertIn("#three", all_tags)


class TestRecursiveDirectoryLoading(unittest.TestCase):
    """Tests for recursive directory loading."""

    def setUp(self):
        """Create a temporary directory structure with FlexTag files."""
        self.temp_dir = tempfile.mkdtemp()

        # Create root level file
        with open(os.path.join(self.temp_dir, "root.flextag"), "w") as f:
            f.write("[[#root_section]]\nRoot content\n[[/]]")

        # Create subdirectory with file
        sub_dir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(sub_dir)
        with open(os.path.join(sub_dir, "sub.ft"), "w") as f:
            f.write("[[#sub_section]]\nSub content\n[[/]]")

        # Create nested subdirectory with file
        nested_dir = os.path.join(sub_dir, "nested")
        os.makedirs(nested_dir)
        with open(os.path.join(nested_dir, "nested.flextag"), "w") as f:
            f.write("[[#nested_section]]\nNested content\n[[/]]")

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_recursive_true_default(self):
        """Test that recursive=True is the default and finds all files."""
        view = FlexTag.load(dir=self.temp_dir, validate=False)
        all_tags = []
        for s in view.sections:
            all_tags.extend(s.tags)
        self.assertEqual(len(view.sections), 3)
        self.assertIn("#root_section", all_tags)
        self.assertIn("#sub_section", all_tags)
        self.assertIn("#nested_section", all_tags)

    def test_recursive_false(self):
        """Test that recursive=False only finds root level files."""
        view = FlexTag.load(dir=self.temp_dir, recursive=False, validate=False)
        all_tags = []
        for s in view.sections:
            all_tags.extend(s.tags)
        self.assertEqual(len(view.sections), 1)
        self.assertIn("#root_section", all_tags)
        self.assertNotIn("#sub_section", all_tags)
        self.assertNotIn("#nested_section", all_tags)

    def test_recursive_with_multiple_dirs(self):
        """Test recursive loading with multiple directories."""
        # Create another temp dir
        other_dir = tempfile.mkdtemp()
        try:
            with open(os.path.join(other_dir, "other.ft"), "w") as f:
                f.write("[[#other_section]]\nOther content\n[[/]]")

            view = FlexTag.load(dir=[self.temp_dir, other_dir], validate=False)
            all_tags = []
            for s in view.sections:
                all_tags.extend(s.tags)
            self.assertEqual(len(view.sections), 4)
            self.assertIn("#other_section", all_tags)
        finally:
            import shutil

            shutil.rmtree(other_dir)

    def test_both_extensions_found(self):
        """Test that both .flextag and .ft files are found."""
        view = FlexTag.load(dir=self.temp_dir, validate=False)
        # root.flextag, sub.ft, nested.flextag
        extensions = []
        for c in view.containers:
            if c.source_name.endswith(".flextag"):
                extensions.append(".flextag")
            elif c.source_name.endswith(".ft"):
                extensions.append(".ft")
        self.assertIn(".flextag", extensions)
        self.assertIn(".ft", extensions)


class TestMetaBlock(unittest.TestCase):
    """Tests for ---meta--- block parsing."""

    def test_meta_block_basic(self):
        """Test basic ---meta--- block parsing."""
        data = """
---meta---
[[#plugin @plugins.chart version=1.0]]
---/meta---

[[#content]]
Hello world
[[/]]
        """
        view = FlexTag.load(string=data, validate=False)
        container = view.containers[0]
        self.assertIn("#plugin", container.tags)
        self.assertIn("#plugins.chart", container.tags)
        self.assertEqual(container.parameters.get("version"), 1.0)

    def test_meta_block_filtering(self):
        """Test that containers can be filtered by meta tags."""
        data = """
---meta---
[[#plugin @plugins.chart]]
---/meta---

[[#content]]
Chart plugin content
[[/]]
        """
        view = FlexTag.load(string=data, validate=False)
        # Container should have the tags from meta block
        self.assertIn("#plugin", view.containers[0].tags)


if __name__ == "__main__":
    unittest.main()
