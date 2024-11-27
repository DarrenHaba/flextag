import gzip
import zipfile
from io import BytesIO

from flextag.core.interfaces.transport import ICompressor
from flextag.logger import logger
from flextag.exceptions import CompressionError


class GzipCompressor(ICompressor):
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


class ZipCompressor(ICompressor):
    """Zip compression implementation"""

    def compress(self, data: str) -> bytes:
        """Compress string data to bytes using zip"""
        try:
            bio = BytesIO()
            with zipfile.ZipFile(bio, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("data", data)
            return bio.getvalue()
        except Exception as e:
            logger.error(f"Zip compression failed: {str(e)}")
            raise CompressionError(f"Zip compression failed: {str(e)}")

    def decompress(self, data: bytes) -> str:
        """Decompress zipped bytes to string"""
        try:
            bio = BytesIO(data)
            with zipfile.ZipFile(bio, "r") as zf:
                return zf.read("data").decode()
        except Exception as e:
            logger.error(f"Zip decompression failed: {str(e)}")
            raise CompressionError(f"Zip decompression failed: {str(e)}")
