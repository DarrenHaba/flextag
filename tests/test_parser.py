import pytest
from flextag import FlexTagParser


def test_json_parser():
    parser = FlexTagParser()
    content = """[[SEC #config {fmt="json"}]]
{
    "port": 8080,
    "debug": true
}
[[/SEC]]"""
    doc = parser.parse(content)
    section = doc.sections[0]
    assert section.content["port"] == 8080
    assert section.content["debug"] is True


def test_yaml_parser():
    parser = FlexTagParser()
    content = """[[SEC #config {fmt="yaml"}]]
server:
  port: 8080
  debug: true
[[/SEC]]"""
    doc = parser.parse(content)
    section = doc.sections[0]
    assert section.content["server"]["port"] == 8080
    assert section.content["server"]["debug"] is True


def test_toml_parser():
    parser = FlexTagParser()
    content = """[[SEC #config {fmt="toml"}]]
[server]
port = 8080
debug = true
[[/SEC]]"""
    doc = parser.parse(content)
    section = doc.sections[0]
    assert section.content["server"]["port"] == 8080
    assert section.content["server"]["debug"] is True


def test_parser_round_trip():
    parser = FlexTagParser()
    original = """[[SEC #data {fmt="json"}]]
{"key": "value"}
[[/SEC]]"""
    doc = parser.parse(original)
    doc.sections[0].content["key"] = "modified"
    result = parser.dump(doc)
    assert '"key": "modified"' in result


def test_custom_parser_registration():
    class CustomParser:
        def parse(self, content):
            return {"parsed": content}

        def dump(self, data):
            return str(data)

    parser = FlexTagParser()
    parser.register_content_parser("custom", CustomParser)

    content = """[[SEC #test {fmt="custom"}]]
test content
[[/SEC]]"""
    doc = parser.parse(content)
    assert doc.sections[0].content == {"parsed": "test content"}
