import pytest
from pathlib import Path
from flextag.managers.base import BaseManager
from flextag.managers.data import DataManager
from flextag.managers.query import QueryManager
from flextag.core.types.block import DataBlock

def test_manager_creation():
    """Test basic manager initialization"""
    data_manager = DataManager()
    assert data_manager.name == "data_manager"
    assert "parsers" in data_manager._registries
    assert "content_handlers" in data_manager._registries

def test_registry_creation():
    """Test registry creation and duplicate handling"""
    manager = BaseManager("test")

    # Test first creation
    manager.create_registry("test_reg")
    assert "test_reg" in manager._registries

    # Test duplicate creation
    manager.create_registry("test_reg")  # Should not raise error

def test_manager_connections():
    """Test manager connections and event flow"""
    data_manager = DataManager()
    query_manager = QueryManager()

    # Connect managers
    data_manager.connect(query_manager)

    # Verify connection
    assert query_manager.name in data_manager._connected_managers

def test_registry_operations():
    """Test registry operations across managers"""
    data_manager = DataManager()

    # Register mock implementation
    mock_parser = object()
    data_manager.register("parsers", "mock", mock_parser)

    # Verify registration
    assert data_manager.get("parsers", "mock") is mock_parser

    # Test missing registry/implementation
    with pytest.raises(ValueError):
        data_manager.get("nonexistent", "mock")
    with pytest.raises(ValueError):
        data_manager.get("parsers", "nonexistent")
