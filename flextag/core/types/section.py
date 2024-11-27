from dataclasses import dataclass
from flextag.core.types.metadata import Metadata
from flextag.logger import logger


@dataclass
class Section:
    """Pure data class for sections"""
    metadata: Metadata
    content: str = ""              # Parsed content
    raw_content: str = ""          # Original unparsed content

    @classmethod
    def create(cls, id: str = "", content: str = "") -> 'Section':
        """Factory method to create a section with default metadata"""
        try:
            metadata = Metadata(id=id)
            return cls(metadata=metadata, content=content, raw_content=content)
        except Exception as e:
            logger.error(f"Failed to create section: {str(e)}")
            raise

    def to_dict(self) -> dict:
        """Convert section to dictionary representation"""
        return {
            "metadata": self.metadata.to_dict(),
            "content": self.content,
            "raw_content": self.raw_content
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Section':
        """Create section from dictionary representation"""
        try:
            return cls(
                metadata=Metadata.from_dict(data["metadata"]),
                content=data.get("content", ""),
                raw_content=data.get("raw_content", "")
            )
        except Exception as e:
            logger.error(f"Failed to create section from dict: {str(e)}")
            raise
