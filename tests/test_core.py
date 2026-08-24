"""FlexTag 0.5 — the format's contract, self-contained (fixtures build their own files)."""
import pytest

import flextag

CONFIG = """---
flextag: 0.5
tags: [config]
id: endpoints
owner: platform
---

# Endpoints

Prose is prose. An untagged fence is an illustration:

```text
this block has no mapping and is NOT a section
```

```yaml {tags: [database, env/production], id: prod-db, version: 2}
host: prod-db.example.com
port: 5432
```

```yaml {tags: [database, env/development], id: dev-db, version: 1}
host: localhost
port: 5432
```
"""

NOTES = """---
tags: [notes]
id: scratch
---

```json {tags: [report], id: columns, version: 1}
{"columns": ["a", "b"]}
```
"""


@pytest.fixture()
def tree(tmp_path):
    (tmp_path / "config.md").write_text(CONFIG, encoding="utf-8")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "notes.md").write_text(NOTES, encoding="utf-8")
    return tmp_path


def test_load_walks_the_tree_and_indexes_everything(tree):
    view = flextag.load(tree)
    assert len(view.docs) == 2 and len(view.sections) == 3


def test_front_matter_is_file_metadata(tree):
    doc = flextag.load(tree).files(tag="config")[0]
    assert doc.meta["owner"] == "platform" and doc.declared == "0.5"
    unmarked = flextag.load(tree).files(tag="notes")[0]
    assert unmarked.declared is None          # loads fine without the marker


def test_filter_by_tag_and_any_key(tree):
    view = flextag.load(tree)
    assert len(view.filter(tag="database").sections) == 2
    hit = view.filter(tag="database", id="prod-db").sections
    assert len(hit) == 1 and hit[0].meta["version"] == 2
    assert hit[0].lang == "yaml" and "prod-db.example.com" in hit[0].body


def test_path_tags_match_any_segment(tree):
    view = flextag.load(tree)
    assert len(view.filter(tag="production").sections) == 1
    assert view.children("env") == ["production", "development"]


def test_values_for_dropdowns(tree):
    assert flextag.load(tree).filter(tag="database").values("id") == ["prod-db", "dev-db"]


def test_untagged_fences_stay_prose(tree):
    view = flextag.load(tree)
    assert all("NOT a section" not in s.body for s in view.sections)


def test_bad_yaml_names_file_and_line(tmp_path):
    f = tmp_path / "bad.md"
    f.write_text("```yaml {tags: [x], id: [unclosed}\nk: v\n```\n", encoding="utf-8")
    with pytest.raises(flextag.FlexTagError) as e:
        flextag.load(f)
    assert "bad.md:1" in str(e.value)


def test_unclosed_fence_is_loud(tmp_path):
    f = tmp_path / "open.md"
    f.write_text("```yaml {tags: [x], id: y}\nnever closed\n", encoding="utf-8")
    with pytest.raises(flextag.FlexTagError):
        flextag.load(f)


def test_json_style_mapping_parses_identically(tmp_path):
    f = tmp_path / "j.md"
    f.write_text('```json {"tags": ["report"], "id": "r", "version": 1}\n{}\n```\n',
                 encoding="utf-8")
    s = flextag.load(f).sections[0]
    assert s.tags == ["report"] and s.meta == {"id": "r", "version": 1}


def test_legacy_reader_still_loads_ft(tmp_path):
    f = tmp_path / "old.ft"
    f.write_text('[[#config id=#a version:int=1]]: yaml\nk: v\n[[/]]\n', encoding="utf-8")
    with pytest.warns(DeprecationWarning):
        from flextag import legacy
        view = legacy.load(path=str(f))
    sec = view.filter("#config").sections[0]
    assert sec.parameters["id"] == "#a"
