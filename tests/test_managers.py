import json

import pytest

from flextag import DataManager
from flextag.managers.base import BaseManager, ManagerEvent
from flextag.managers.query import QueryManager
from flextag.core.types.block import DataBlock


def test_base_manager_events():
    """Test basic event emission and handling"""
    manager = BaseManager("test")
    events_received = []

    def handle_event(event: ManagerEvent):
        events_received.append(event)

    manager.subscribe("test_event", handle_event)
    manager.emit("test_event", {"data": "test"})

    assert len(events_received) == 1
    assert events_received[0].source == "test"
    assert events_received[0].data["data"] == "test"


def test_base_manager_registry():
    """Test registry functionality"""
    manager = BaseManager("test")

    # Test registration
    manager.register("test_registry", "item1", "value1")
    assert manager.get("test_registry", "item1") == "value1"

    # Test missing registry
    with pytest.raises(ValueError):
        manager.get("missing", "item")

    # Test missing implementation
    with pytest.raises(ValueError):
        manager.get("test_registry", "missing")


def test_query_manager_initialization():
    """Test QueryManager setup"""
    manager = QueryManager()

    # Verify DuckDB setup
    result = manager.conn.execute("SELECT COUNT(*) FROM blocks").fetchone()
    assert result[0] == 0

    # Verify indexes
    indexes = manager.conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND sql IS NOT NULL
    """).fetchall()
    assert len(indexes) == 2


def test_query_manager_block_handling():
    """Test block event handling and storage"""
    manager = QueryManager()

    # Create test block
    block = DataBlock(
        id="test1",
        tags=["tag1", "tag2"],
        paths=["path.to.test"],
        parameters={"format": "json"},
        content_start=1,
        content_end=3
    )

    # Simulate block_parsed event
    manager.handle_block_parsed(ManagerEvent(
        source="data_manager",
        event_type="block_parsed",
        data={"block": block}
    ))

    # Verify block was stored
    result = manager.conn.execute("SELECT * FROM blocks").fetchone()
    assert result is not None
    assert result[0] == "test1"  # block_id
    assert "tag1" in result[2]   # tags
    assert "tag2" in result[2]   # tags
    assert "path.to.test" in result[3]  # paths


def test_query_manager_search():
    """Test search functionality"""
    manager = QueryManager()

    # Add test data
    block = DataBlock(
        id="test1",
        tags=["tag1"],
        paths=["path.test"],
        parameters={"format": "json"},
        content_start=1,
        content_end=3
    )

    manager.handle_block_parsed(ManagerEvent(
        source="data_manager",
        event_type="block_parsed",
        data={"block": block}
    ))

    # Mock query parser
    class MockQueryParser:
        def to_sql(self, query: str) -> str:
            return "SELECT * FROM blocks WHERE block_id = 'test1'"

    manager.register("query_parsers", "default", MockQueryParser())

    # Test search
    results = manager.search(":test1")
    assert len(results) == 1
    assert results[0]["block_id"] == "test1"


def test_manager_connections():
    """Test manager interconnection and event propagation"""
    manager1 = BaseManager("manager1")
    manager2 = BaseManager("manager2")

    events_received = []

    def handle_event(event: ManagerEvent):
        events_received.append(event)

    manager2.subscribe("test_event", handle_event)
    manager1.connect(manager2)

    manager1.emit("test_event", {"data": "test"})

    assert len(events_received) == 1
    assert events_received[0].source == "manager1"


def test_manager_event_handling():
    """Test event propagation between managers"""
    # Setup
    data_manager = DataManager()
    query_manager = QueryManager()

    # Initialize test block
    test_block = DataBlock(
        id="test1",
        tags=["example"],
        paths=[],
        parameters={},
        content_start=1,
        content_end=1
    )

    # Track each step
    events_received = []
    blocks_processed = []
    db_operations = []

    def test_handler(event):
        events_received.append(event)
        try:
            block = event.data["block"]
            blocks_processed.append(block.id)

            # Attempt DB insert
            query_manager.conn.execute("""
                INSERT INTO blocks (
                    block_id, file_path, tags, paths, parameters, 
                    content_start, content_end
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                block.id,
                None,
                block.tags,
                block.paths,
                json.dumps(block.parameters),
                block.content_start,
                block.content_end
            ])
            db_operations.append("insert_success")
        except Exception as e:
            db_operations.append(f"insert_failed: {str(e)}")

    # Connect everything
    query_manager._event_handlers = [test_handler]
    query_manager.subscribe("block_parsed", test_handler)
    data_manager.connect(query_manager)

    # Emit event
    data_manager.emit("block_parsed", {"block": test_block})

    # Verify each step
    print("\nEvent propagation test results:")
    print(f"Events received: {len(events_received)}")
    print(f"Blocks processed: {blocks_processed}")
    print(f"DB operations: {db_operations}")

    # Check database content
    rows = query_manager.conn.execute("SELECT * FROM blocks").fetchall()
    print(f"Database rows: {rows}")

    # Original assertions
    assert len(events_received) == 1, "Event wasn't received"
    assert len(blocks_processed) == 1, "Block wasn't processed"
    assert blocks_processed[0] == "test1", "Wrong block processed"
    assert db_operations[0] == "insert_success", "DB insert failed"

    count = query_manager.conn.execute("SELECT COUNT(*) FROM blocks").fetchone()[0]
    assert count == 1, f"Expected 1 row in database, found {count}"


def test_duckdb_initialization():
    """Test DuckDB setup"""
    query_manager = QueryManager()

    # Check table exists
    tables = query_manager.conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='blocks'
    """).fetchall()

    assert len(tables) == 1, "blocks table not created"

    # Check table schema
    schema = query_manager.conn.execute("DESCRIBE blocks").fetchall()
    print("\nTable schema:")
    for col in schema:
        print(f"Column: {col}")

    # Verify we can insert
    test_data = {
        "block_id": "test",
        "file_path": None,
        "tags": ["tag1"],
        "paths": [],
        "parameters": "{}",
        "content_start": 1,
        "content_end": 1
    }

    query_manager.conn.execute("""
        INSERT INTO blocks (
            block_id, file_path, tags, paths, parameters, 
            content_start, content_end
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, list(test_data.values()))

    count = query_manager.conn.execute("SELECT COUNT(*) FROM blocks").fetchone()[0]
    assert count == 1, "Test insert failed"