from flextag import Section


def test_section_creation():
    section = Section(
        tags=["draft", "review"],
        paths=["docs.guide"],
        params={"priority": 1},
        content="Test content",
    )
    assert section.tags == ["draft", "review"]
    assert section.paths == ["docs.guide"]
    assert section.params == {"priority": 1}
    assert section.content == "Test content"


def test_section_from_header():
    header = "[[SEC #draft #review .docs.guide {priority=1}]]"
    section = Section.from_header(header, "Test content")
    assert section.tags == ["draft", "review"]
    assert section.paths == ["docs.guide"]
    assert section.params == {"priority": 1}
    assert section.content == "Test content"


def test_section_matches():
    section = Section(
        tags=["draft", "review"], paths=["docs.guide"], content="Test content"
    )
    assert section.matches("#draft")
    assert section.matches(".docs")
    assert section.matches("#draft .docs")
    assert not section.matches("#published")


def test_section_matches_exact():
    section = Section(tags=["draft"], paths=["docs.guide"], content="Test content")
    assert section.matches(".docs.guide", match_type="exact")
    assert not section.matches(".docs", match_type="exact")


def test_param_type_inference():
    header = '[[SEC {str="value", int=42, float=3.14, bool=true}]]'
    section = Section.from_header(header)
    assert section.params["str"] == "value"
    assert section.params["int"] == 42
    assert section.params["float"] == 3.14
    assert section.params["bool"] is True
