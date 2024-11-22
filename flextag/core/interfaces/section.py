from typing import Protocol, Dict, List, Any
from dataclasses import dataclass


class ISection(Protocol):
    """Interface for self-contained FlexTag sections"""

    id: str  # Section identifier
    tags: List[str]  # Section tags
    paths: List[str]  # Section paths
    parameters: Dict[str, Any]  # Custom parameters
    content: str  # Section content

    # Required parameters (always present)
    fmt: str  # Content format
    enc: str  # Content encoding
    crypt: str  # Encryption method
    comp: str  # Compression method
    lang: str  # Content language

    def matches(self, query: str) -> bool:
        """Check if section matches query"""
        ...

    def clone(self) -> "ISection":
        """Create independent copy of section"""
        ...

    @classmethod
    def from_header(cls, header: str, content: str = "") -> "ISection":
        """Create section from header and content"""
        ...
