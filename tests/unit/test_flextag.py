import importlib.util
import os
import tempfile
import unittest

from flextag import FlexTag, SchemaValidationError

HAS_FTML = importlib.util.find_spec("ftml") is not None

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

    def test_descendant_match_with_double_star(self):
        """Test that #tag.** in schema matches all descendant tags."""
        data = """
[[#schema.product.**]]: ftml-schema
name: str
[[/]]

[[#schema.product.laptop name="ThinkPad"]]: text
Laptop matches because schema uses ** for descendants
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

    def test_immediate_children_with_dot_star(self):
        """Test that #tag.* matches immediate children only."""
        data = """
[[#adapter.*]]: ftml-schema
name: str
[[/]]

[[#adapter.live name="Binance"]]: text
One level deep — matches
[[/]]

[[#adapter.live.binance name="Deep"]]: text
Two levels deep — should NOT match the .* schema
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

        # Filter by tag OR path (legacy OR keyword)
        filtered = view.filter("#final OR @development")
        self.assertEqual(len(filtered.sections), 2)
        all_tags = []
        for s in filtered.sections:
            all_tags.extend(s.tags)
        self.assertIn("#two", all_tags)
        self.assertIn("#three", all_tags)

        # Filter by tag | path (pipe syntax)
        filtered = view.filter("#final | @development")
        self.assertEqual(len(filtered.sections), 2)
        all_tags = []
        for s in filtered.sections:
            all_tags.extend(s.tags)
        self.assertIn("#two", all_tags)
        self.assertIn("#three", all_tags)


class TestPipeAndGrouping(unittest.TestCase):
    """Tests for | (OR) and () grouping in filters and schemas."""

    def test_pipe_or_in_filter(self):
        """| works as OR in filter queries."""
        data = """
[[#a]]: text
A
[[/]]

[[#b]]: text
B
[[/]]

[[#c]]: text
C
[[/]]
        """
        view = FlexTag.load(string=data, validate=False)
        result = view.filter("#a | #b")
        self.assertEqual(len(result.sections), 2)

    def test_pipe_or_three_alternatives(self):
        """| with three alternatives."""
        data = """
[[#a]]: text
A
[[/]]

[[#b]]: text
B
[[/]]

[[#c]]: text
C
[[/]]
        """
        view = FlexTag.load(string=data, validate=False)
        result = view.filter("#a | #b | #c")
        self.assertEqual(len(result.sections), 3)

    def test_group_or_in_filter(self):
        """() group with | works as AND with OR-group."""
        data = """
[[#stock #nyse]]: text
NYSE stock
[[/]]

[[#stock #nasdaq]]: text
NASDAQ stock
[[/]]

[[#etf #nyse]]: text
NYSE ETF
[[/]]

[[#stock #arca]]: text
ARCA stock
[[/]]
        """
        view = FlexTag.load(string=data, validate=False)
        # Must be #stock AND one of (#nyse | #nasdaq)
        result = view.filter("#stock (#nyse | #nasdaq)")
        self.assertEqual(len(result.sections), 2)
        tags = [s.tags[0] for s in result.sections]
        self.assertIn("#stock", tags)

    def test_group_or_in_schema(self):
        """Schema with () group validates correctly."""
        data = """
[[#product.* (#electronics | #clothing)]]: ftml-schema
name: str
[[/]]

[[#product.laptop #electronics name="ThinkPad"]]: text
Valid — has #electronics
[[/]]

[[#product.shirt #clothing name="T-Shirt"]]: text
Valid — has #clothing
[[/]]

[[#product.food #grocery name="Apple"]]: text
No matching schema — #grocery not in group
[[/]]

[[#product.food #grocery]]: text
No schema applies, no name required
[[/]]
        """
        view = FlexTag.load(string=data, validate=True)
        data_sections = [s for s in view.sections if s.type_name != "ftml-schema"]
        self.assertEqual(len(data_sections), 4)

    def test_schema_group_validation_failure(self):
        """Schema with () group rejects missing required field."""
        data = """
[[#product.* (#electronics | #clothing)]]: ftml-schema
name: str
[[/]]

[[#product.laptop #electronics]]: text
Missing name — should fail validation
[[/]]
        """
        with self.assertRaises(Exception):
            FlexTag.load(string=data, validate=True)

    def test_group_negation_inside(self):
        """Negation works inside () groups."""
        data = """
[[#a #x]]: text
A with X
[[/]]

[[#a #y]]: text
A with Y
[[/]]

[[#a #z]]: text
A with Z
[[/]]
        """
        view = FlexTag.load(string=data, validate=False)
        # Must have #a AND one of (#x | #y) — #z excluded
        result = view.filter("#a (#x | #y)")
        self.assertEqual(len(result.sections), 2)

    def test_pipe_replaces_or_keyword(self):
        """| and OR keyword both work."""
        data = """
[[#a]]: text
A
[[/]]

[[#b]]: text
B
[[/]]
        """
        view = FlexTag.load(string=data, validate=False)
        result_pipe = view.filter("#a | #b")
        result_or = view.filter("#a OR #b")
        self.assertEqual(len(result_pipe.sections), len(result_or.sections))


class TestWildcardSyntax(unittest.TestCase):
    """Tests for glob-style wildcard syntax: *, .*, .**"""

    def setUp(self):
        """Create a dataset with hierarchical tags for wildcard testing."""
        self.data = """
[[#exchange]]: text
The exchange parent
[[/]]

[[#exchange.nasdaq]]: text
NASDAQ exchange
[[/]]

[[#exchange.nyse]]: text
NYSE exchange
[[/]]

[[#exchange.nasdaq.aapl]]: text
AAPL under NASDAQ
[[/]]

[[#exchange.nasdaq.msft]]: text
MSFT under NASDAQ
[[/]]

[[#foo]]: text
Foo
[[/]]

[[#foobar]]: text
Foobar
[[/]]

[[#food]]: text
Food
[[/]]

[[#for]]: text
For
[[/]]

[[#four]]: text
Four
[[/]]
        """
        self.view = FlexTag.load(string=self.data, validate=False)

    # ── Character wildcard: #fo* ──

    def test_char_wildcard_matches_prefix(self):
        """#fo* matches any tag starting with 'fo'."""
        result = self.view.filter("#fo*")
        tags = [s.tags[0] for s in result.sections]
        self.assertIn("#foo", tags)
        self.assertIn("#foobar", tags)
        self.assertIn("#food", tags)
        self.assertIn("#for", tags)
        self.assertIn("#four", tags)

    def test_char_wildcard_does_not_cross_dots(self):
        """#fo* should NOT match hierarchical tags like #foo.bar."""
        result = self.view.filter("#fo*")
        tags = [s.tags[0] for s in result.sections]
        # Should not include #exchange.nasdaq.aapl etc.
        for t in tags:
            self.assertNotIn(".", t.lstrip("#"))

    def test_char_wildcard_no_match(self):
        """#zz* matches nothing."""
        result = self.view.filter("#zz*")
        self.assertEqual(len(result.sections), 0)

    def test_char_wildcard_exact_prefix(self):
        """#exchange* matches #exchange only (not #exchange.nasdaq)."""
        result = self.view.filter("#exchange*")
        self.assertEqual(len(result.sections), 1)
        self.assertIn("#exchange", result.sections[0].tags)

    def test_char_wildcard_case_insensitive(self):
        """#FO* matches tags starting with 'fo' (case-insensitive)."""
        result = self.view.filter("#FO*")
        tags = [s.tags[0] for s in result.sections]
        self.assertIn("#foo", tags)
        self.assertIn("#food", tags)

    # ── Hierarchy one level: #tag.* ──

    def test_one_level_matches_direct_children(self):
        """#exchange.* matches direct children only."""
        result = self.view.filter("#exchange.*")
        tags = [s.tags[0] for s in result.sections]
        self.assertIn("#exchange.nasdaq", tags)
        self.assertIn("#exchange.nyse", tags)
        self.assertEqual(len(result.sections), 2)

    def test_one_level_excludes_self(self):
        """#exchange.* does NOT match #exchange itself."""
        result = self.view.filter("#exchange.*")
        tags = [s.tags[0] for s in result.sections]
        self.assertNotIn("#exchange", tags)

    def test_one_level_excludes_grandchildren(self):
        """#exchange.* does NOT match #exchange.nasdaq.aapl."""
        result = self.view.filter("#exchange.*")
        tags = [s.tags[0] for s in result.sections]
        self.assertNotIn("#exchange.nasdaq.aapl", tags)
        self.assertNotIn("#exchange.nasdaq.msft", tags)

    def test_one_level_deeper(self):
        """#exchange.nasdaq.* matches AAPL and MSFT."""
        result = self.view.filter("#exchange.nasdaq.*")
        tags = [s.tags[0] for s in result.sections]
        self.assertIn("#exchange.nasdaq.aapl", tags)
        self.assertIn("#exchange.nasdaq.msft", tags)
        self.assertEqual(len(result.sections), 2)

    # ── Hierarchy any depth: #tag.** ──

    def test_any_depth_matches_all_descendants(self):
        """#exchange.** matches everything under exchange."""
        result = self.view.filter("#exchange.**")
        tags = [s.tags[0] for s in result.sections]
        self.assertIn("#exchange.nasdaq", tags)
        self.assertIn("#exchange.nyse", tags)
        self.assertIn("#exchange.nasdaq.aapl", tags)
        self.assertIn("#exchange.nasdaq.msft", tags)
        self.assertEqual(len(result.sections), 4)

    def test_any_depth_excludes_self(self):
        """#exchange.** does NOT match #exchange itself."""
        result = self.view.filter("#exchange.**")
        tags = [s.tags[0] for s in result.sections]
        self.assertNotIn("#exchange", tags)

    def test_any_depth_from_deeper(self):
        """#exchange.nasdaq.** matches only AAPL and MSFT."""
        result = self.view.filter("#exchange.nasdaq.**")
        tags = [s.tags[0] for s in result.sections]
        self.assertIn("#exchange.nasdaq.aapl", tags)
        self.assertIn("#exchange.nasdaq.msft", tags)
        self.assertEqual(len(result.sections), 2)

    # ── Combined: hierarchy + character wildcard ──

    def test_combined_hierarchy_and_char(self):
        """#exchange.na* matches children starting with 'na'."""
        result = self.view.filter("#exchange.na*")
        tags = [s.tags[0] for s in result.sections]
        self.assertIn("#exchange.nasdaq", tags)
        self.assertNotIn("#exchange.nyse", tags)

    def test_combined_hierarchy_and_char_no_match(self):
        """#exchange.zz* matches nothing."""
        result = self.view.filter("#exchange.zz*")
        self.assertEqual(len(result.sections), 0)

    # ── Exact match unchanged ──

    def test_exact_match_still_works(self):
        """#exchange.nasdaq matches exactly."""
        result = self.view.filter("#exchange.nasdaq")
        self.assertEqual(len(result.sections), 1)
        self.assertIn("#exchange.nasdaq", result.sections[0].tags)

    def test_exact_match_no_descendants(self):
        """#exchange does NOT match #exchange.nasdaq."""
        result = self.view.filter("#exchange")
        self.assertEqual(len(result.sections), 1)
        self.assertIn("#exchange", result.sections[0].tags)

    # ── Negation unchanged ──

    def test_negation_still_works(self):
        """!#foo excludes sections with #foo."""
        result = self.view.filter("!#foo")
        tags = [s.tags[0] for s in result.sections]
        self.assertNotIn("#foo", tags)

    # ── Schema with new wildcards ──

    def test_schema_double_star(self):
        """Schema with .** validates all descendants."""
        data = """
[[#item.**]]: ftml-schema
name: str
[[/]]

[[#item.book name="Moby Dick"]]: text
Valid
[[/]]

[[#item.book.chapter name="Loomings"]]: text
Also valid — deeper descendant
[[/]]
        """
        view = FlexTag.load(string=data, validate=True)
        data_sections = [s for s in view.sections if s.type_name != "ftml-schema"]
        self.assertEqual(len(data_sections), 2)

    def test_schema_single_star(self):
        """Schema with .* validates direct children only."""
        data = """
[[#item.*]]: ftml-schema
name: str
[[/]]

[[#item.book name="Moby Dick"]]: text
Valid — direct child
[[/]]

[[#item.book.chapter name="Loomings"]]: text
NOT validated — two levels deep
[[/]]

[[#item.book.chapter]]: text
No name — fine because schema doesn't apply at this depth
[[/]]
        """
        view = FlexTag.load(string=data, validate=True)
        data_sections = [s for s in view.sections if s.type_name != "ftml-schema"]
        self.assertEqual(len(data_sections), 3)


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


class TestFileMetadata(unittest.TestCase):
    """Tests for file-metadata section parsing."""

    def test_file_metadata_basic(self):
        """Test basic file-metadata section parsing."""
        data = """
[[#plugin #plugins.chart version=1.0]]: file-metadata
[[/]]

[[#content]]
Hello world
[[/]]
        """
        view = FlexTag.load(string=data, validate=False)
        container = view.containers[0]
        self.assertIn("#plugin", container.tags)
        self.assertIn("#plugins.chart", container.tags)
        self.assertEqual(container.parameters.get("version"), 1.0)

    def test_file_metadata_filtering(self):
        """Test that containers can be filtered by file-metadata tags."""
        data = """
[[#plugin #plugins.chart]]: file-metadata
[[/]]

[[#content]]
Chart plugin content
[[/]]
        """
        view = FlexTag.load(string=data, validate=False)
        # Container should have the tags from file-metadata section
        self.assertIn("#plugin", view.containers[0].tags)


class TestSchemaContentType(unittest.TestCase):
    """Tests for the 'schema' content type (metadata-only validation)."""

    @requires_ftml
    def test_schema_validates_header_only(self):
        """schema type validates header params but ignores body content."""
        data = """
[[#product.*]]: schema
name: str
[[/]]

[[#product.electronics name="Keyboard"]]: ftml
description = "Mechanical keyboard"
random_field = 42
[[/]]
        """
        # Should pass — schema only checks header params, body is irrelevant
        view = FlexTag.load(string=data, validate=True)
        sections = view.sections
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0].parameters["name"], "Keyboard")

    @requires_ftml
    def test_schema_does_not_validate_body(self):
        """schema type should NOT validate FTML body content."""
        data = """
[[#item.*]]: schema
name: str
price: float
[[/]]

[[#item.widget name="Widget" price=9.99]]: ftml
name = 42
price = "not a number"
[[/]]
        """
        # Should pass — body content is NOT validated by schema type
        # (body has wrong types but schema ignores body)
        view = FlexTag.load(string=data, validate=True)
        self.assertEqual(len(view.sections), 1)

    @requires_ftml
    def test_schema_empty_body(self):
        """Empty schema body = tag-matching only, no property validation."""
        data = """
[[#product.* (#electronics | #clothing)]]: schema
[[/]]

[[#product.laptop #electronics name="MacBook"]]: ftml
price = 2499.99
[[/]]
        """
        # Should pass — empty schema body means just check tags match
        view = FlexTag.load(string=data, validate=True)
        self.assertEqual(len(view.sections), 1)

    @requires_ftml
    def test_schema_and_ftml_schema_both_apply(self):
        """A section can match both schema and ftml-schema."""
        data = """
[[#product.* (#electronics | #clothing)]]: schema
[[/]]

[[#product.*]]: ftml-schema
name: str
[[/]]

[[#product.laptop #electronics name="MacBook"]]: ftml
name = "MacBook Pro"
[[/]]
        """
        # Both schemas apply — schema checks tags, ftml-schema checks header+body
        view = FlexTag.load(string=data, validate=True)
        self.assertEqual(len(view.sections), 1)

    def test_schema_sections_excluded_from_results(self):
        """Schema sections should not appear in view.sections or filter results."""
        data = """
[[#product.*]]: schema
[[/]]

[[#product.*]]: ftml-schema
name: str
[[/]]

[[#product.laptop name="MacBook"]]: text
A laptop
[[/]]
        """
        view = FlexTag.load(string=data, validate=True)
        # Only the data section should appear
        self.assertEqual(len(view.sections), 1)
        self.assertEqual(view.sections[0].parameters["name"], "MacBook")


class TestStrictMode(unittest.TestCase):
    """Tests for strict=True validation mode."""

    @requires_ftml
    def test_strict_passes_all_matched(self):
        """All sections match a schema — no error."""
        data = """
[[#product.*]]: ftml-schema
name: str
[[/]]

[[#product.laptop name="MacBook"]]: text
A laptop
[[/]]

[[#product.phone name="iPhone"]]: text
A phone
[[/]]
        """
        view = FlexTag.load(string=data, validate=True, strict=True)
        self.assertEqual(len(view.sections), 2)

    def test_strict_fails_unmatched(self):
        """Section matching zero schemas raises error in strict mode."""
        data = """
[[#product.*]]: ftml-schema
name: str
[[/]]

[[#product.laptop name="MacBook"]]: text
A laptop
[[/]]

[[#notes]]: text
Random notes
[[/]]
        """
        with self.assertRaises(SchemaValidationError) as ctx:
            FlexTag.load(string=data, validate=True, strict=True)
        self.assertIn("Strict mode", str(ctx.exception))

    def test_strict_skips_schema_sections(self):
        """Schema and ftml-schema sections are exempt from strict check."""
        data = """
[[#product.*]]: schema
[[/]]

[[#product.*]]: ftml-schema
name: str
[[/]]

[[#product.laptop name="MacBook"]]: text
A laptop
[[/]]
        """
        # Should pass — schema sections don't need to match a schema
        view = FlexTag.load(string=data, validate=True, strict=True)
        self.assertEqual(len(view.sections), 1)

    def test_strict_skips_file_metadata(self):
        """file-metadata sections are exempt from strict check."""
        data = """
[[#myfile version="1.0"]]: file-metadata
[[/]]

[[#product.*]]: ftml-schema
name: str
[[/]]

[[#product.laptop name="MacBook"]]: text
A laptop
[[/]]
        """
        view = FlexTag.load(string=data, validate=True, strict=True)
        self.assertEqual(len(view.sections), 1)

    def test_strict_off_by_default(self):
        """Without strict=True, unmatched sections are fine."""
        data = """
[[#product.*]]: ftml-schema
name: str
[[/]]

[[#product.laptop name="MacBook"]]: text
A laptop
[[/]]

[[#notes]]: text
Random notes
[[/]]
        """
        # Should pass — strict is off by default
        view = FlexTag.load(string=data, validate=True)
        self.assertEqual(len(view.sections), 2)

    def test_strict_no_schemas_fails(self):
        """Strict mode with no schemas at all should fail if sections exist."""
        data = """
[[#notes]]: text
Random notes
[[/]]
        """
        with self.assertRaises(SchemaValidationError) as ctx:
            FlexTag.load(string=data, validate=True, strict=True)
        self.assertIn("Strict mode", str(ctx.exception))


class TestParameterConstraints(unittest.TestCase):
    """Tests for parameter constraints in schema headers."""

    @requires_ftml
    def test_header_constraint_syntax(self):
        """Schema header with constraint defs validates matching sections."""
        data = """
[[#item.* name:str]]: schema
[[/]]

[[#item.widget name="Widget"]]: text
A widget
[[/]]
        """
        view = FlexTag.load(string=data, validate=True)
        self.assertEqual(len(view.sections), 1)

    @requires_ftml
    def test_header_constraint_with_body_defs(self):
        """Header constraint defs merge with body property definitions."""
        data = """
[[#item.* name:str]]: ftml-schema
price: float
[[/]]

[[#item.widget name="Widget" price=9.99]]: ftml
name = "Widget Pro"
price = 9.99
[[/]]
        """
        view = FlexTag.load(string=data, validate=True)
        self.assertEqual(len(view.sections), 1)

    @requires_ftml
    def test_header_constraint_validation_failure(self):
        """Missing required field from header constraint raises error."""
        data = """
[[#item.* name:str]]: schema
[[/]]

[[#item.widget]]: text
A widget without a name
[[/]]
        """
        with self.assertRaises(SchemaValidationError):
            FlexTag.load(string=data, validate=True)


if __name__ == "__main__":
    unittest.main()
