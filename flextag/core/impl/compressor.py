import gzip
import zipfile
from io import BytesIO
from ..base.compressor import BaseCompressor
from ...exceptions import CompressionError
from ...logger import logger


class GzipCompressor(BaseCompressor):
    """Gzip compression implementation"""

    def compress(self, data: str) -> bytes:
        try:
            return gzip.compress(data.encode())
        except Exception as e:
            logger.error(f"Gzip compression failed: {str(e)}")
            raise CompressionError(f"Gzip compression failed: {str(e)}")

    def decompress(self, data: bytes) -> str:
        try:
            return gzip.decompress(data).decode()
        except Exception as e:
            logger.error(f"Gzip decompression failed: {str(e)}")
            raise CompressionError(f"Gzip decompression failed: {str(e)}")


class ZipCompressor(BaseCompressor):
    """Zip compression implementation"""

    def compress(self, data: str) -> bytes:
        try:
            bio = BytesIO()
            with zipfile.ZipFile(bio, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("data", data)
            return bio.getvalue()
        except Exception as e:
            logger.error(f"Zip compression failed: {str(e)}")
            raise CompressionError(f"Zip compression failed: {str(e)}")

    def decompress(self, data: bytes) -> str:
        try:
            bio = BytesIO(data)
            with zipfile.ZipFile(bio, "r") as zf:
                return zf.read("data").decode()
        except Exception as e:
            logger.error(f"Zip decompression failed: {str(e)}")
            raise CompressionError(f"Zip decompression failed: {str(e)}")
