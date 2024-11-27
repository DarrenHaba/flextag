import gzip
from flextag.core.base.compressor import BaseCompressor
from flextag.logger import logger
from flextag.exceptions import CompressionError


class GzipCompressor(BaseCompressor):
    """GZip compression implementation"""

    def compress(self, data: str) -> bytes:
        """Compress string data to bytes using gzip"""
        try:
            return gzip.compress(data.encode())
        except Exception as e:
            logger.error(f"Gzip compression failed: {str(e)}")
            raise CompressionError(f"Gzip compression failed: {str(e)}")

    def decompress(self, data: bytes) -> str:
        """Decompress gzipped bytes to string"""
        try:
            return gzip.decompress(data).decode()
        except Exception as e:
            logger.error(f"Gzip decompression failed: {str(e)}")
            raise CompressionError(f"Gzip decompression failed: {str(e)}")
