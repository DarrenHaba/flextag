import pytest
from flextag.core.compression.comp_gzip import GzipCompressor
from flextag.core.compression.comp_zip import ZipCompressor
from flextag.core.compression.registry import CompressionRegistry
from flextag.exceptions import CompressionError

# Add more test cases?
# Add performance benchmarks?
# Add specific edge cases?


class TestCompressors:
    """Test individual compressor implementations"""

    @pytest.fixture
    def test_data(self) -> str:
        """Sample data for compression tests"""
        return """This is test data that should compress well.
        It has repeated content content content content
        and multiple lines lines lines lines
        to ensure good compression ratio."""

    @pytest.fixture
    def binary_data(self) -> bytes:
        """Sample binary data for compression tests"""
        return bytes(range(256))  # All possible byte values

    def test_gzip_compression(self, test_data):
        """Test GZip compression and decompression"""
        compressor = GzipCompressor()

        # Test compression
        compressed = compressor.compress(test_data)
        assert isinstance(compressed, bytes)
        assert len(compressed) < len(test_data.encode())

        # Test decompression
        decompressed = compressor.decompress(compressed)
        assert isinstance(decompressed, str)
        assert decompressed == test_data

    def test_zip_compression(self, test_data):
        """Test Zip compression and decompression"""
        compressor = ZipCompressor()

        # Test compression
        compressed = compressor.compress(test_data)
        assert isinstance(compressed, bytes)
        assert len(compressed) < len(test_data.encode())

        # Test decompression
        decompressed = compressor.decompress(compressed)
        assert isinstance(decompressed, str)
        assert decompressed == test_data

    def test_compression_ratio(self, test_data):
        """Test compression ratios of different algorithms"""
        gzip_compressor = GzipCompressor()
        zip_compressor = ZipCompressor()

        gzip_compressed = gzip_compressor.compress(test_data)
        zip_compressed = zip_compressor.compress(test_data)

        # Both should achieve significant compression
        assert len(gzip_compressed) < len(test_data.encode()) * 0.8
        assert len(zip_compressed) < len(test_data.encode()) * 0.8

    def test_empty_data(self):
        """Test compression of empty data"""
        compressors = [GzipCompressor(), ZipCompressor()]

        for compressor in compressors:
            compressed = compressor.compress("")
            decompressed = compressor.decompress(compressed)
            assert decompressed == ""

    def test_binary_data(self, binary_data):
        """Test compression of binary data"""
        compressors = [GzipCompressor(), ZipCompressor()]

        for compressor in compressors:
            # Convert binary to string for compression
            data = binary_data.hex()
            compressed = compressor.compress(data)
            decompressed = compressor.decompress(compressed)
            assert decompressed == data

    def test_unicode_data(self):
        """Test compression of Unicode data"""
        test_data = "Hello 你好 Γειά σας こんにちは 안녕하세요"
        compressors = [GzipCompressor(), ZipCompressor()]

        for compressor in compressors:
            compressed = compressor.compress(test_data)
            decompressed = compressor.decompress(compressed)
            assert decompressed == test_data

    def test_invalid_data(self):
        """Test handling of invalid data"""
        compressors = [GzipCompressor(), ZipCompressor()]

        for compressor in compressors:
            # Test invalid compressed data
            with pytest.raises(CompressionError):
                compressor.decompress(b"invalid data")


class TestCompressionRegistry:
    """Test compression registry functionality"""

    @pytest.fixture(autouse=True)
    def setup_registry(self):
        """Setup and cleanup registry for each test"""
        CompressionRegistry.clear()
        yield
        CompressionRegistry.clear()

    def test_registration(self):
        """Test registering compressors"""
        # Register compressors
        CompressionRegistry.register("gzip", GzipCompressor())
        CompressionRegistry.register("zip", ZipCompressor())

        # Check registration
        assert "gzip" in CompressionRegistry.list_compressors()
        assert "zip" in CompressionRegistry.list_compressors()

    def test_get_compressor(self):
        """Test getting registered compressors"""
        gzip_compressor = GzipCompressor()
        CompressionRegistry.register("gzip", gzip_compressor)

        # Get registered compressor
        retrieved = CompressionRegistry.get("gzip")
        assert retrieved == gzip_compressor

        # Test getting nonexistent compressor
        with pytest.raises(CompressionError):
            CompressionRegistry.get("nonexistent")

    def test_active_compressor(self):
        """Test active compressor management"""
        # Register compressors
        CompressionRegistry.register("gzip", GzipCompressor())
        CompressionRegistry.register("zip", ZipCompressor())

        # Test default active (first registered)
        active = CompressionRegistry.get_active()
        assert isinstance(active, GzipCompressor)

        # Change active compressor
        CompressionRegistry.set_active("zip")
        active = CompressionRegistry.get_active()
        assert isinstance(active, ZipCompressor)

        # Test invalid active setting
        with pytest.raises(CompressionError):
            CompressionRegistry.set_active("nonexistent")

    def test_unregistration(self):
        """Test unregistering compressors"""
        # Register and then unregister
        CompressionRegistry.register("gzip", GzipCompressor())
        CompressionRegistry.unregister("gzip")

        # Check removal
        assert "gzip" not in CompressionRegistry.list_compressors()

        # Test unregistering nonexistent
        with pytest.raises(CompressionError):
            CompressionRegistry.unregister("nonexistent")

    def test_clear_registry(self):
        """Test clearing registry"""
        # Register compressors
        CompressionRegistry.register("gzip", GzipCompressor())
        CompressionRegistry.register("zip", ZipCompressor())

        # Clear registry
        CompressionRegistry.clear()

        # Check if cleared
        assert len(CompressionRegistry.list_compressors()) == 0
        with pytest.raises(CompressionError):
            CompressionRegistry.get_active()


@pytest.mark.integration
class TestCompressionIntegration:
    """Integration tests for compression system"""

    @pytest.fixture
    def sample_data(self):
        """Large sample data for integration tests"""
        return "x" * 1000 + "y" * 1000 + "z" * 1000

    def test_compression_workflow(self, sample_data):
        """Test complete compression workflow"""
        # Register compressors
        CompressionRegistry.register("gzip", GzipCompressor())
        CompressionRegistry.register("zip", ZipCompressor())

        # Test with each compressor
        for name in ["gzip", "zip"]:
            CompressionRegistry.set_active(name)
            compressor = CompressionRegistry.get_active()

            # Compress and decompress
            compressed = compressor.compress(sample_data)
            decompressed = compressor.decompress(compressed)

            # Verify
            assert decompressed == sample_data
            assert len(compressed) < len(sample_data)

    def test_compression_switching(self, sample_data):
        """Test switching between compression algorithms"""
        # Register compressors
        CompressionRegistry.register("gzip", GzipCompressor())
        CompressionRegistry.register("zip", ZipCompressor())

        # Compress with gzip
        CompressionRegistry.set_active("gzip")
        gzip_compressed = CompressionRegistry.get_active().compress(sample_data)

        # Compress with zip
        CompressionRegistry.set_active("zip")
        zip_compressed = CompressionRegistry.get_active().compress(sample_data)

        # Verify different results
        assert gzip_compressed != zip_compressed

        # Verify both decompress correctly
        assert CompressionRegistry.get("gzip").decompress(gzip_compressed) == sample_data
        assert CompressionRegistry.get("zip").decompress(zip_compressed) == sample_data
