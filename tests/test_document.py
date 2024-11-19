import pytest
from flextag import Document, Section


def test_document_creation():
    doc = Document()
    assert doc.settings == {}
    assert doc.info is None
    assert doc.sections == []


def test_document_settings():
    content = """[[SETTINGS {enc="utf-8", fmt="yaml"}]]"""
    doc = Document.from_string(content)
    assert doc.settings == {"enc": "utf-8", "fmt": "yaml"}


def test_document_info():
    content = """[[INFO #meta {version="1.0"}]]
Info content
[[/INFO]]"""
    doc = Document.from_string(content)
    assert doc.info is not None
    assert doc.info.tags == ["meta"]
    assert doc.info.params == {"version": "1.0"}
    assert doc.info.content == "Info content"


def test_document_sections():
    content = """[[SEC #test .path {priority=1}]]
Test content
[[/SEC]]"""
    doc = Document.from_string(content)
    assert len(doc.sections) == 1
    assert doc.sections[0].tags == ["test"]
    assert doc.sections[0].paths == ["path"]
    assert doc.sections[0].params == {"priority": 1}


def test_document_find():
    doc = Document()
    doc.add_section(Section(tags=["draft"], paths=["docs.guide"]))
    doc.add_section(Section(tags=["published"], paths=["docs.api"]))

    assert len(doc.find("#draft")) == 1
    assert len(doc.find(".docs")) == 2
    assert len(doc.find("#published .docs.api")) == 1


def test_document_to_string():
    doc = Document()
    doc.settings = {"fmt": "yaml"}
    doc.info = Section(tags=["meta"], content="Info")
    doc.add_section(Section(tags=["test"], content="Test"))

    result = doc.to_string()
    assert "[[SETTINGS" in result
    assert "[[INFO #meta]]" in result
    assert "[[SEC #test]]" in result
