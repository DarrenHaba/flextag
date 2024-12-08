import pytest
from pathlib import Path
from flextag.core.content.handler import ContentHandler
from flextag.core.content.provider import ContentProvider
from flextag.managers.data import DataManager

def test_content_loading():
    """Test basic content loading"""
    handler = ContentHandler()

    # Create test file
    test_file = Path("test.flextag")
    test_file.write_text("""[[DATA:test1]]
line1
line2
line3
[[/DATA]]""")

    try:
        content = handler.get_content("test1", test_file, (2, 4))
        assert content == "line1\nline2\nline3"
    finally:
        handler.close()  # Close handles before cleanup
        test_file.unlink()

def test_file_handle_management():
    """Test file handle cleanup"""
    handler = ContentHandler()

    # Create test files
    files = []
    for i in range(3):
        file = Path(f"test{i}.flextag")
        file.write_text(f"content{i}")
        files.append(file)

    try:
        # Access files
        for file in files:
            handler.get_content("test", file, (1, 1))
    finally:
        handler.close()  # Close handles
        for file in files:
            file.unlink()

def test_content_provider():
    """Test content provider with manager"""
    data_manager = DataManager()
    provider = ContentProvider()

    data_manager.register("content_handlers", "default", provider)

    # Setup test data
    test_file = Path("test.flextag")
    test_file.write_text("""[[DATA:test1]]
content
[[/DATA]]""")

    try:
        content = data_manager.get_content(
            block_id="test1",
            content_range=(2, 2),
            file_path=str(test_file)
        )
        assert content == "content"
    finally:
        provider.close()
        test_file.unlink()

def test_handler_cleanup():
    """Test automatic file handle cleanup"""
    handler = ContentHandler()

    test_file = Path("test.flextag")
    test_file.write_text("test content")

    try:
        # Access file
        handler.get_content("test", test_file, (1, 1))

        # Verify handle exists
        assert str(test_file) in handler._file_handles

        # Close handles
        handler.close()

        # Verify cleanup
        assert not handler._file_handles
    finally:
        test_file.unlink()
