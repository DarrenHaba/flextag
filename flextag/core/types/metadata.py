from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class Metadata:
    """Core metadata structure for data blocks"""
    # Required fields
    id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    paths: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)

    # Optional fields
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    format: str = "text"           # Content format (text, json, yaml, etc)
    encoding: str = "utf-8"        # Content encoding
    compression: str = ""          # Compression method if used
    encryption: str = ""           # Encryption method if used
    version: str = "1.0"          # Metadata version

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "id": self.id,
            "tags": self.tags.copy(),
            "paths": self.paths.copy(),
            "parameters": self.parameters.copy(),
            "created": self.created.isoformat() if self.created else None,
            "modified": self.modified.isoformat() if self.modified else None,
            "format": self.format,
            "encoding": self.encoding,
            "compression": self.compression,
            "encryption": self.encryption,
            "version": self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Metadata':
        """Create metadata from dictionary"""
        # Parse dates if present
        created = (
            datetime.fromisoformat(data["created"])
            if data.get("created")
            else None
        )
        modified = (
            datetime.fromisoformat(data["modified"])
            if data.get("modified")
            else None
        )

        return cls(
            id=data.get("id"),
            tags=data.get("tags", []).copy(),
            paths=data.get("paths", []).copy(),
            parameters=data.get("parameters", {}).copy(),
            created=created,
            modified=modified,
            format=data.get("format", "text"),
            encoding=data.get("encoding", "utf-8"),
            compression=data.get("compression", ""),
            encryption=data.get("encryption", ""),
            version=data.get("version", "1.0")
        )


@dataclass
class TransportMetadata(Metadata):
    """Extended metadata for transport containers"""
    checksum: str = ""           # Content checksum
    transport_version: str = "1.0"  # Transport format version
    source_file: Optional[str] = None  # Original file if from file
    chunk_size: int = 0         # For chunked transfers
    total_chunks: int = 0       # For chunked transfers
    chunk_index: int = 0        # For chunked transfers

    def to_dict(self) -> Dict[str, Any]:
        """Convert transport metadata to dictionary"""
        data = super().to_dict()
        data.update({
            "checksum": self.checksum,
            "transport_version": self.transport_version,
            "source_file": self.source_file,
            "chunk_size": self.chunk_size,
            "total_chunks": self.total_chunks,
            "chunk_index": self.chunk_index
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransportMetadata':
        """Create transport metadata from dictionary"""
        metadata = super().from_dict(data)
        return cls(
            **metadata.__dict__,
            checksum=data.get("checksum", ""),
            transport_version=data.get("transport_version", "1.0"),
            source_file=data.get("source_file"),
            chunk_size=data.get("chunk_size", 0),
            total_chunks=data.get("total_chunks", 0),
            chunk_index=data.get("chunk_index", 0)
        )
