# Implementation Plan: Tag Paths

All changes in `src/flextag/flextag.py`. Tests in `tests/unit/test_metadata/test_tags.py`.

## Step 1: Rewrite `_match_pattern()` (line 322-329)

Replace exact match with segment-based chain matching. Both `pat` and `tag` arrive lowercase, no `#` prefix.

**Logic:**
- Split `tag` on `#` → tag segments (e.g. `"exchange#nyse#aapl"` → `["exchange", "nyse", "aapl"]`)
- Check if `pat` ends with `#` → trailing-hash mode (direct children only)
- Split `pat` on `#` (stripping trailing empty from trailing `#`) → pattern segments
- Handle inline OR groups: if any pattern segment contains `(`, it's an OR group like `(nyse|nasdaq)` — expand alternatives
- If pattern is a single segment: match if it appears anywhere in tag segments
- If pattern is multi-segment: match if it appears as a contiguous sub-sequence in tag segments
- If trailing `#`: the matched sub-sequence must be followed by exactly one more segment and that must be the end of the chain

## Step 2: Update `match_tag()` docstring (line 301-319)

Update docstring to describe segment-based matching. No logic change — it already delegates to `_match_pattern()`.

## Step 3: Handle inline OR groups in `parse_query()` (line 238-261)

The tokenizer currently stops at `(` when reading a regular token (line 258: `query[j] not in " \t("`). A chain like `#symbol#(nyse|nasdaq)#aapl` would be split into `#symbol#` and `(nyse|nasdaq)#aapl`.

**Fix:** When reading a regular token, if we encounter `(`, continue through the matching `)` and keep going until whitespace.

## Step 4: Add `.children(tag, depth=1)` to FlexView (after line 1828)

- Scan all section tags in the view
- For each tag, split into segments on `#`
- Find where the query segments match as a contiguous sub-sequence
- Extract segments that follow the match position
- `depth=1`: flat `list[str]` of unique next-level segments
- `depth>1`: nested `dict` going N levels deep
- `depth=0`: nested `dict` all the way to leaves

## Step 5: Add `.parents(tag, depth=1)` to FlexView (after `.children()`)

- Same scan but looks backward from the match position
- `depth=1`: flat `list[str]` of unique parent segments
- `depth>1`: nested `dict` going N levels up
- `depth=0`: nested `dict` all the way to roots

## Step 6: Add tests

17 test cases covering:
- Segment matching (single, contiguous, non-contiguous rejection, order matters)
- Trailing `#` (direct children, deeper exclusion)
- Inline OR groups
- `.children()` at depth 1, 2, 0, scoped
- `.parents()` at depth 1, 0, root returns empty
- Schema matching with chains
- Filter AND/OR/negation with chains
- Backward compat: flat tags still work

## What does NOT change

- Tag storage (Section.raw_tags) — stored exactly as written
- `.tags()` method — returns tags as-is
- `.values()` method — unrelated (parameters)
- Schema validation — uses `match_tag()`, gets chain support automatically
- Filter query operators (AND, OR, negation, grouping) — operate on tokens, matching is per-token
