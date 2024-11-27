import zipfile
from io import BytesIO
from flextag.core.base.compressor import BaseCompressor
from flextag.logger import logger
from flextag.exceptions import CompressionError


class ZipCompressor(BaseCompressor):
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
