import pytest
from flextag import parse
from flextag.exceptions import MissingWrapperError, InvalidTagError, StructureError


def test_basic_parsing():
    content = """<<--FLEXTAG_START-->>
    <<--[test]:
    Hello World
<<--FLEXTAG_END-->>"""
    assert parse(content) == {"test": "Hello World"}


def test_missing_start_marker():
    content = """    <<--[test]:
    Hello World
<<--FLEXTAG_END-->>"""
    with pytest.raises(MissingWrapperError):
        parse(content)


def test_missing_end_marker():
    content = """<<--FLEXTAG_START-->>
    <<--[test]:
    Hello World"""
    with pytest.raises(MissingWrapperError):
        parse(content)


def test_incorrect_content_indentation():
    content = """<<--FLEXTAG_START-->>
    <<--[test]:
Wrong indent  # No indentation
<<--FLEXTAG_END-->>"""
    with pytest.raises(StructureError):
        parse(content)


def test_list_output():
    content = """<<--FLEXTAG_START-->>
    <<--[0]:
    First
    <<--[1]:
    Second
<<--FLEXTAG_END-->>"""
    assert parse(content) == ["First", "Second"]


def test_malformed_tag():
    content = """<<--FLEXTAG_START-->>
    <<--test]:  # Malformed tag - missing opening bracket
    Content here
<<--FLEXTAG_END-->>"""
    with pytest.raises(InvalidTagError):
        parse(content)
