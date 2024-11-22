from ..interfaces.compressor import ICompressor
from ..impl.compressor import GzipCompressor, ZipCompressor
from .registry import CompressionRegistry

# Register default compressors
CompressionRegistry.register('gzip', GzipCompressor)
CompressionRegistry.register('zip', ZipCompressor)

__all__ = [
    'ICompressor',
    'GzipCompressor',
    'ZipCompressor',
    'CompressionRegistry',
]
