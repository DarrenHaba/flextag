from flextag import FlexTagParser


def test_complete_document():
    content = """[[SETTINGS {fmt="yaml"}]]

[[INFO #meta .docs {fmt="toml"}]]
title = "Test Document"
version = "1.0"
[[/INFO]]

[[SEC #config .settings {fmt="json"}]]
{
    "port": 8080,
    "debug": true
}
[[/SEC]]

[[SEC #users .data {fmt="yaml"}]]
users:
  - name: John
    role: admin
[[/SEC]]"""

    parser = FlexTagParser()
    doc = parser.parse(content)

    # Check settings
    assert doc.settings["fmt"] == "yaml"

    # Check info
    assert doc.info.content["title"] == "Test Document"
    assert doc.info.content["version"] == "1.0"

    # Check sections
    config = doc.find_one("#config")
    assert config.content["port"] == 8080
    assert config.content["debug"] is True

    users = doc.find_one("#users")
    assert users.content["users"][0]["name"] == "John"
    assert users.content["users"][0]["role"] == "admin"


def test_modify_and_save():
    parser = FlexTagParser()
    doc = parser.parse(
        """[[SEC #data {fmt="json"}]]
{"items": []}
[[/SEC]]"""
    )

    # Modify content
    section = doc.find_one("#data")
    section.content["items"].append("new item")

    # Save and reload
    content = parser.dump(doc)
    new_doc = parser.parse(content)

    # Verify changes persisted
    assert "new item" in new_doc.find_one("#data").content["items"]


def test_multiple_formats():
    test_data = {
        "json": '{"key": "value"}',
        "yaml": "key: value",
        "toml": "key = 'value'",
    }

    parser = FlexTagParser()
    for fmt, content in test_data.items():
        doc = parser.parse(
            f"""[[SEC #test {{fmt="{fmt}"}}]]
{content}
[[/SEC]]"""
        )

        section = doc.find_one("#test")
        assert section.content["key"] == "value"
