import pytest

from flextag.legacy import FlexTag, _match_pattern, match_tag, parse_query


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


# ──────────────────────────────────────────────────────────────────────────
# Tag Paths — segment-based matching
# ──────────────────────────────────────────────────────────────────────────


class TestMatchPattern:
    """Unit tests for _match_pattern (both args lowercase, no # prefix)."""

    def test_single_segment_match_leaf(self):
        assert _match_pattern("aapl", "exchange#nyse#aapl")

    def test_single_segment_match_middle(self):
        assert _match_pattern("nyse", "exchange#nyse#aapl")

    def test_single_segment_match_root(self):
        assert _match_pattern("exchange", "exchange#nyse#aapl")

    def test_contiguous_subchain_start(self):
        assert _match_pattern("exchange#nyse", "exchange#nyse#aapl")

    def test_contiguous_subchain_end(self):
        assert _match_pattern("nyse#aapl", "exchange#nyse#aapl")

    def test_exact_match(self):
        assert _match_pattern("exchange#nyse#aapl", "exchange#nyse#aapl")

    def test_non_contiguous_segments_rejected(self):
        """Segments must be adjacent — exchange#aapl skips nyse."""
        assert not _match_pattern("exchange#aapl", "exchange#nyse#aapl")

    def test_reversed_order_rejected(self):
        """Order matters — aapl#exchange doesn't match exchange#...#aapl."""
        assert not _match_pattern("aapl#exchange", "exchange#nyse#aapl")

    def test_no_match(self):
        assert not _match_pattern("missing", "exchange#nyse#aapl")

    def test_flat_tag_exact(self):
        """Flat tags (no chain) still work — backward compat."""
        assert _match_pattern("draft", "draft")

    def test_flat_tag_no_partial(self):
        """Segment matching, not substring matching."""
        assert not _match_pattern("dra", "draft")


class TestTrailingHash:
    """Trailing # = direct children only."""

    def test_trailing_hash_one_level(self):
        assert _match_pattern("adapter#", "adapter#ohlcv")

    def test_trailing_hash_too_deep(self):
        assert not _match_pattern("adapter#", "adapter#ohlcv#yahoo")

    def test_trailing_hash_exact_is_not_child(self):
        """A tag that IS the pattern (no extra segment) should not match."""
        assert not _match_pattern("adapter#", "adapter")

    def test_trailing_hash_mid_chain(self):
        """Trailing hash on a sub-chain."""
        assert _match_pattern("exchange#nyse#", "exchange#nyse#aapl")
        assert not _match_pattern("exchange#nyse#", "exchange#nyse#aapl#options")

    def test_trailing_hash_single_segment(self):
        """#adapter# should match #adapter#X but not #adapter alone."""
        assert _match_pattern("adapter#", "adapter#news")
        assert not _match_pattern("adapter#", "adapter")


class TestInlineORGroups:
    """Inline OR groups in chain patterns."""

    def test_or_group_match(self):
        assert _match_pattern("symbol#(nyse|nasdaq)#aapl", "symbol#nyse#aapl")

    def test_or_group_second_alt(self):
        assert _match_pattern("symbol#(nyse|nasdaq)#aapl", "symbol#nasdaq#aapl")

    def test_or_group_no_match(self):
        assert not _match_pattern("symbol#(nyse|nasdaq)#aapl", "symbol#arca#aapl")

    def test_or_group_with_trailing_hash(self):
        assert _match_pattern(
            "symbol#(nyse|nasdaq|arca)#", "symbol#nyse#aapl"
        )
        assert not _match_pattern(
            "symbol#(nyse|nasdaq|arca)#", "symbol#nyse#aapl#options"
        )

    def test_or_group_spaces(self):
        """Spaces inside OR group are allowed."""
        assert _match_pattern("symbol#(nyse | nasdaq)#aapl", "symbol#nyse#aapl")


class TestParseQueryChains:
    """parse_query correctly tokenizes inline OR groups in chains."""

    def test_chain_with_or_group_is_single_token(self):
        result = parse_query("#symbol#(nyse|nasdaq)#aapl")
        assert result == [["#symbol#(nyse|nasdaq)#aapl"]]

    def test_chain_with_or_group_and_trailing_hash(self):
        result = parse_query("#symbol#(nyse|nasdaq)#")
        assert result == [["#symbol#(nyse|nasdaq)#"]]

    def test_chain_or_group_in_and_expression(self):
        result = parse_query("#symbol#(nyse|nasdaq)# #active")
        assert result == [["#symbol#(nyse|nasdaq)#", "#active"]]

    def test_standalone_paren_group_still_works(self):
        """Parenthesized OR group NOT in a chain stays as separate token."""
        result = parse_query("#adapter (#ohlcv | #news)")
        assert result == [["#adapter", "(#ohlcv | #news)"]]


class TestMatchTagChains:
    """Integration test for match_tag with # prefix handling."""

    def test_match_tag_segment(self):
        assert match_tag("#aapl", ["#exchange#nyse#aapl"])

    def test_match_tag_subchain(self):
        assert match_tag("#exchange#nyse", ["#exchange#nyse#aapl"])

    def test_match_tag_trailing_hash(self):
        assert match_tag("#exchange#", ["#exchange#nyse"])
        assert not match_tag("#exchange#", ["#exchange#nyse#aapl"])

    def test_match_tag_case_insensitive(self):
        assert match_tag("#AAPL", ["#Exchange#NYSE#aapl"])
        assert match_tag("#exchange", ["#EXCHANGE#NYSE#AAPL"])


class TestFilterChains:
    """End-to-end filter tests using FlexTag parsing."""

    @pytest.fixture
    def view(self):
        content = """\
[[#exchange#nyse#aapl]]
apple
[[/]]

[[#exchange#nyse#goog]]
google
[[/]]

[[#exchange#nasdaq#msft]]
microsoft
[[/]]

[[#adapter#ohlcv#yahoo]]
yahoo adapter
[[/]]

[[#adapter#ohlcv]]
base ohlcv
[[/]]

[[#adapter#news]]
news adapter
[[/]]
"""
        return FlexTag.load(string=content)

    def test_filter_segment(self, view):
        result = view.filter("#aapl")
        assert len(result.sections) == 1

    def test_filter_all_exchange(self, view):
        result = view.filter("#exchange")
        assert len(result.sections) == 3

    def test_filter_direct_children(self, view):
        """#adapter# should match sections with exactly one segment after adapter."""
        result = view.filter("#adapter#")
        names = [s.content.strip() for s in result.sections]
        assert "base ohlcv" in names
        assert "news adapter" in names
        assert "yahoo adapter" not in names
        assert len(result.sections) == 2

    def test_filter_subchain(self, view):
        result = view.filter("#exchange#nyse")
        assert len(result.sections) == 2

    def test_filter_and(self, view):
        """AND: segment + trailing hash."""
        result = view.filter("#adapter #ohlcv")
        # Both #adapter#ohlcv#yahoo and #adapter#ohlcv have both segments
        assert len(result.sections) == 2

    def test_filter_or(self, view):
        result = view.filter("#aapl | #msft")
        assert len(result.sections) == 2

    def test_filter_negation(self, view):
        result = view.filter("#exchange !#nyse")
        assert len(result.sections) == 1
        assert result.sections[0].content.strip() == "microsoft"

    def test_flat_tag_still_works(self):
        """A section with a flat tag (no chain) still matches exactly."""
        content = """\
[[#draft]]
some content
[[/]]
"""
        view = FlexTag.load(string=content)
        assert len(view.filter("#draft").sections) == 1
        assert len(view.filter("#missing").sections) == 0


class TestSchemaChains:
    """Schema matching uses match_tag, so chains work automatically."""

    def test_schema_matches_chain(self):
        content = """\
[[#adapter]]: ftml-schema
description: str
[[/]]

[[#adapter#ohlcv#yahoo name="Yahoo"]]: ftml
description = "provider"
[[/]]
"""
        # Should parse without validation errors — schema matches via segment
        view = FlexTag.load(string=content)
        assert len(view.sections) == 1
        assert view.sections[0].parameters["name"] == "Yahoo"

    def test_schema_trailing_hash_direct_children(self):
        content = """\
[[#adapter#]]: ftml-schema
adapter_type: str
[[/]]

[[#adapter#ohlcv]]: ftml
adapter_type = "market"
[[/]]

[[#adapter#ohlcv#yahoo]]: ftml
deeper_info = "yahoo details"
[[/]]
"""
        # #adapter# schema matches #adapter#ohlcv (direct child) ✓
        # #adapter# schema does NOT match #adapter#ohlcv#yahoo (too deep)
        # So strict mode should reject the deeper section
        from flextag.legacy import SchemaValidationError
        with pytest.raises(SchemaValidationError):
            FlexTag.load(string=content, strict=True)

        # In non-strict mode both load fine
        view2 = FlexTag.load(string=content, strict=False)
        assert len(view2.sections) == 2


class TestChildrenMethod:
    """Tests for FlexView.children()."""

    @pytest.fixture
    def view(self):
        content = """\
[[#make#ford#mustang#gt]]
1
[[/]]
[[#make#ford#mustang#svt]]
2
[[/]]
[[#make#ford#f150#xlt]]
3
[[/]]
[[#make#ford#f150#lariat]]
4
[[/]]
[[#make#dodge#charger#rt]]
5
[[/]]
[[#color#ford#blue]]
6
[[/]]
"""
        return FlexTag.load(string=content)

    def test_children_depth1(self, view):
        result = view.children("#make")
        assert result == ["ford", "dodge"]

    def test_children_depth1_scoped(self, view):
        result = view.children("#make#ford")
        assert result == ["mustang", "f150"]

    def test_children_unscoped_ford(self, view):
        """#ford appears under #make and #color, so both subtrees contribute."""
        result = view.children("#ford")
        assert "mustang" in result
        assert "f150" in result
        assert "blue" in result

    def test_children_depth2(self, view):
        result = view.children("#ford", depth=2)
        assert result == {
            "mustang": ["gt", "svt"],
            "f150": ["lariat", "xlt"],
            "blue": [],
        }

    def test_children_depth0(self, view):
        result = view.children("#make#ford", depth=0)
        assert result == {
            "mustang": {"gt": {}, "svt": {}},
            "f150": {"xlt": {}, "lariat": {}},
        }

    def test_children_leaf_returns_empty(self, view):
        result = view.children("#gt")
        assert result == []


class TestParentsMethod:
    """Tests for FlexView.parents()."""

    @pytest.fixture
    def view(self):
        content = """\
[[#make#ford#mustang#gt]]
1
[[/]]
[[#make#ford#mustang#svt]]
2
[[/]]
[[#make#ford#f150#xlt]]
3
[[/]]
[[#color#ford#blue]]
4
[[/]]
"""
        return FlexTag.load(string=content)

    def test_parents_depth1(self, view):
        result = view.parents("#ford")
        assert result == ["make", "color"]

    def test_parents_root_returns_empty(self, view):
        result = view.parents("#make")
        assert result == []

    def test_parents_depth0(self, view):
        result = view.parents("#gt", depth=0)
        assert result == {"mustang": {"ford": {"make": {}}}}

    def test_parents_scoped_full_path(self, view):
        """Full chain match at root — no segments precede it, so empty."""
        result = view.parents("#make#ford#mustang#gt")
        assert result == []

    def test_parents_scoped_partial_path(self, view):
        """Partial chain match — segments before the match are parents."""
        result = view.parents("#ford#mustang#gt")
        assert result == ["make"]
