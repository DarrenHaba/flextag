import pytest
from flextag.managers.query import QueryManager
from flextag.managers.base import ManagerEvent
from flextag.core.types.block import DataBlock


class TestQuerySystem:
    @pytest.fixture
    def query_manager(self):
        """Initialize query manager for testing"""
        return QueryManager()

    @pytest.fixture
    def sample_blocks(self):
        return [
            DataBlock(
                id="movie1",
                tags=["scifi", "action"],
                paths=["movies.scifi", "movies.action"],
                parameters={"year": 1999, "rating": 5},
                content_start=1,
                content_end=3
            ),
            DataBlock(
                id="movie2",
                tags=["horror", "scifi"],
                paths=["movies.horror"],
                parameters={"year": 1979, "rating": 4},
                content_start=4,
                content_end=6
            ),
            DataBlock(
                id="doc1",
                tags=["documentation"],
                paths=["docs.technical"],
                parameters={"format": "markdown", "version": 1.0},
                content_start=7,
                content_end=9
            )
        ]

    def add_blocks(self, manager, blocks):
        """Helper to add blocks to manager"""
        for block in blocks:
            manager.handle_block_parsed(ManagerEvent(
                source="test",
                event_type="block_parsed",
                data={"block": block}
            ))
        manager.flush()  # Process any pending blocks

    def test_block_storage(self, query_manager, sample_blocks):
        """Verify blocks are being stored correctly"""
        self.add_blocks(query_manager, sample_blocks)
    
        # Debug storage state
        print("\nStorage State:")
        print(f"Block IDs: {query_manager.block_ids}")
        print(f"Pending blocks: {len(query_manager.pending_blocks)}")
        print(f"Unique tags: {query_manager.unique_tags}")
        print(f"Tag matrix shape: {query_manager.tag_matrix.shape if query_manager.tag_matrix is not None else None}")
    
        # Verify core arrays
        assert len(query_manager.block_ids) == 3
        assert len(query_manager.unique_tags) > 0
        assert len(query_manager.unique_paths) > 0
    
        # Verify matrices were created
        assert query_manager.tag_matrix is not None
        assert query_manager.tag_matrix.shape == (3, len(query_manager.unique_tags))

    def test_tag_search(self, query_manager, sample_blocks):
        """Test basic tag searching"""
        self.add_blocks(query_manager, sample_blocks)

        # Debug info
        print("\nDebug - Before search:")
        print(f"Unique tags: {query_manager.unique_tags}")
        print(f"Tag matrix shape: {query_manager.tag_matrix.shape}")
        print(f"Tag matrix:\n{query_manager.tag_matrix}")

        # Single tag
        results = query_manager.search("#scifi")

        # Debug info
        print("\nAfter search:")
        print(f"Query: #scifi")
        print(f"Results: {results}")

        assert len(results) == 2
        assert {"movie1", "movie2"} == {r["block_id"] for r in results}

    def test_path_search(self, query_manager, sample_blocks):
        """Test path searching"""
        self.add_blocks(query_manager, sample_blocks)

        # Debug info
        print("\nDebug - Before search:")
        print(f"Unique paths: {query_manager.unique_paths}")
        print(f"Path matrix shape: {query_manager.path_matrix.shape}")
        print(f"Path matrix:\n{query_manager.path_matrix}")

        # Exact path
        results = query_manager.search(".movies.horror")

        # Debug info
        print("\nAfter search:")
        print(f"Query: .movies.horror")
        print(f"Results: {results}")

        assert len(results) == 1
        assert results[0]["block_id"] == "movie2"

    def test_parameter_search(self, query_manager, sample_blocks):
        """Test parameter searching"""
        self.add_blocks(query_manager, sample_blocks)
    
        # Debug parameter storage
        print("\nParameter Storage:")
        print(f"Parameter arrays: {query_manager.param_arrays}")
        print(f"Parameter objects: {query_manager.param_objects}")
    
        # Debug Year search
        print("\nYear Search:")
        results = query_manager.search("year = 1999")
        print(f"Year search results: {results}")
        assert len(results) == 1
        assert results[0]["block_id"] == "movie1"
    
        # Debug Format search
        print("\nFormat Search:")
        print(f"Format parameter array: {query_manager.param_arrays.get('format')}")
        results = query_manager.search('format = "markdown"')
        print(f"Format search results: {results}")
        assert len(results) == 1
        assert results[0]["block_id"] == "doc1"

    def test_combined_search(self, query_manager, sample_blocks):
        """Test combined search conditions"""
        self.add_blocks(query_manager, sample_blocks)

        # Tag AND Path
        results = query_manager.search("#scifi AND .movies.action")
        assert len(results) == 1
        assert results[0]["block_id"] == "movie1"

        # Tag AND Parameter
        results = query_manager.search("#scifi AND rating = 5")
        assert len(results) == 1
        assert results[0]["block_id"] == "movie1"

    def test_wildcard_search(self, query_manager, sample_blocks):
        """Test wildcard searching"""
        self.add_blocks(query_manager, sample_blocks)

        # Tag wildcard
        results = query_manager.search("#sci*")
        assert len(results) == 2

        # Path wildcard
        results = query_manager.search(".*.technical")
        assert len(results) == 1
        assert results[0]["block_id"] == "doc1"

    def test_matrix_growth(self, query_manager):
        """Test matrix handling during growth"""
        # Add blocks incrementally
        block1 = DataBlock(id="test1", tags=["tag1"], paths=["path1"])
        block2 = DataBlock(id="test2", tags=["tag2"], paths=["path2"])

        query_manager.handle_block_parsed(ManagerEvent(
            source="test",
            event_type="block_parsed",
            data={"block": block1}
        ))

        # Verify first block
        results = query_manager.search("#tag1")
        assert len(results) == 1

        # Add second block
        query_manager.handle_block_parsed(ManagerEvent(
            source="test",
            event_type="block_parsed",
            data={"block": block2}
        ))

        # Verify both blocks
        results = query_manager.search("#tag1")
        assert len(results) == 1
        results = query_manager.search("#tag2")
        assert len(results) == 1

    def test_parameter_types(self, query_manager):
        """Test handling of different parameter types"""
        block = DataBlock(
            id="test",
            parameters={
                "int_val": 42,
                "float_val": 3.14,
                "str_val": "test",
                "bool_val": True,
                "null_val": None
            }
        )

        query_manager.handle_block_parsed(ManagerEvent(
            source="test",
            event_type="block_parsed",
            data={"block": block}
        ))

        # Test each type
        assert len(query_manager.search("int_val = 42")) == 1
        assert len(query_manager.search("float_val = 3.14")) == 1
        assert len(query_manager.search('str_val = "test"')) == 1
        assert len(query_manager.search("bool_val = true")) == 1

    def test_error_handling(self, query_manager):
        """Test error handling in queries"""
        # Invalid tag format (no # prefix)
        with pytest.raises(ValueError):
            query_manager.search("tag1")  # Missing # prefix

        # Invalid path format (no . prefix)
        with pytest.raises(ValueError):
            query_manager.search("path/to/something")  # Missing . prefix

        # Invalid parameter format
        with pytest.raises(ValueError):
            query_manager.search("year:1999")  # Using : instead of =

        # Empty query
        with pytest.raises(ValueError):
            query_manager.search("")

    def test_empty_results(self, query_manager, sample_blocks):
        """Test handling of queries with no matches"""
        self.add_blocks(query_manager, sample_blocks)

        results = query_manager.search("#nonexistent")
        assert len(results) == 0

        results = query_manager.search(".nonexistent.path")
        assert len(results) == 0

        results = query_manager.search("nonexistent = 0")
        assert len(results) == 0

    def test_case_sensitivity(self, query_manager):
        """Test case sensitivity handling"""
        block = DataBlock(
            id="Test",
            tags=["Tag", "TAG"],
            paths=["Path.One", "PATH.TWO"],
            parameters={"Key": "Value"}
        )

        query_manager.handle_block_parsed(ManagerEvent(
            source="test",
            event_type="block_parsed",
            data={"block": block}
        ))

        # Test various case combinations
        assert len(query_manager.search("#Tag")) == 1
        assert len(query_manager.search("#TAG")) == 1
        assert len(query_manager.search(".Path.One")) == 1
        assert len(query_manager.search(".PATH.TWO")) == 1
        assert len(query_manager.search('Key = "Value"')) == 1

    def test_query_performance(self, query_manager):
        """Basic performance test"""
        # Generate test blocks
        for i in range(1000):
            block = DataBlock(
                id=f"perf_{i}",
                tags=[f"tag_{i % 10}"],
                paths=[f"path.{i % 5}"],
                parameters={"index": i}
            )
            query_manager.handle_block_parsed(ManagerEvent(
                source="test",
                event_type="block_parsed",
                data={"block": block}
            ))

        # Verify quick response for various queries
        import time

        start = time.time()
        results = query_manager.search("#tag_1")
        assert time.time() - start < 0.1  # Should be very fast
        assert len(results) == 100  # 10% of blocks

        start = time.time()
        results = query_manager.search(".path.1")
        assert time.time() - start < 0.1
        assert len(results) == 200  # 20% of blocks