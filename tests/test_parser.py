from flextag.core.parser.streaming import StreamingParser
from flextag.core.parser.provider import ParserProvider
from flextag.managers.data import DataManager

def test_basic_block_parsing():
    """Test parsing of a simple data block"""
    parser = StreamingParser()

    test_data = """[[DATA:test1 #tag1 .path1]]
Content
[[/DATA]]"""

    blocks = list(parser.parse_stream(test_data.splitlines()))
    assert len(blocks) == 1
    assert blocks[0].id == "test1"
    assert blocks[0].tags == ["tag1"]
    assert blocks[0].paths == ["path1"]
    assert blocks[0].content_start == 2
    assert blocks[0].content_end == 2

def test_parameters_parsing():
    """Test parsing of block parameters"""
    parser = StreamingParser()

    test_data = """[[DATA:test1 {"format": "json", "version": 1.0}]]
{}
[[/DATA]]"""

    blocks = list(parser.parse_stream(test_data.splitlines()))
    assert blocks[0].parameters["format"] == "json"
    assert blocks[0].parameters["version"] == 1.0

def test_multiple_blocks():
    """Test parsing multiple blocks"""
    parser = StreamingParser()

    test_data = """[[DATA:block1]]
content1
[[/DATA]]

[[DATA:block2]]
content2
[[/DATA]]"""

    blocks = list(parser.parse_stream(test_data.splitlines()))
    assert len(blocks) == 2
    assert blocks[0].id == "block1"
    assert blocks[1].id == "block2"

def test_self_closing_block():
    """Test parsing of self-closing blocks"""
    parser = StreamingParser()

    test_data = """[[DATA:empty #tag]/]]"""

    blocks = list(parser.parse_stream(test_data.splitlines()))
    assert len(blocks) == 1
    assert blocks[0].content_start == blocks[0].content_end

def test_parser_provider():
    """Test parser provider with manager"""
    data_manager = DataManager()
    provider = ParserProvider()

    # Register provider
    data_manager.register("parsers", "default", provider)

    # Test parsing
    test_data = """[[DATA:test]]
content
[[/DATA]]"""

    data_manager.parse_string(test_data)
    # Verification will depend on event handling setup
