from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from flextag.core.types.metadata import Metadata
from flextag.core.types.section import Section
from flextag.logger import logger


@dataclass
class Container:
    """Pure data class for container"""
    params: Dict[str, Any] = field(default_factory=dict)     # [[PARAMS]] data
    metadata: Metadata = field(default_factory=Metadata)      # [[META]] data
    sections: List[Section] = field(default_factory=list)     # [[SEC]] sections
    raw_content: str = ""                                    # Original unparsed content

    @classmethod
    def create(cls) -> 'Container':
        """Factory method to create an empty container"""
        try:
            return cls(
                params={},
                metadata=Metadata(),
                sections=[],
                raw_content=""
            )
        except Exception as e:
            logger.error(f"Failed to create container: {str(e)}")
            raise

    def add_section(self, section: Section) -> None:
        """Add a section to the container"""
        try:
            if section not in self.sections:  # Avoid duplicates
                self.sections.append(section)
                logger.debug(
                    f"Added section: id={section.metadata.id}, "
                    f"tags={section.metadata.tags}, "
                    f"paths={section.metadata.paths}"
                )
        except Exception as e:
            logger.error(f"Failed to add section: {str(e)}")
            raise

    def get_section(self, id: str) -> Optional[Section]:
        """Get section by ID"""
        try:
            for section in self.sections:
                if section.metadata.id == id:
                    return section
            return None
        except Exception as e:
            logger.error(f"Failed to get section: {str(e)}")
            raise

    def to_dict(self) -> dict:
        """Convert container to dictionary representation"""
        return {
            "params": self.params.copy(),
            "metadata": self.metadata.to_dict(),
            "sections": [section.to_dict() for section in self.sections],
            "raw_content": self.raw_content
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Container':
        """Create container from dictionary representation"""
        try:
            container = cls(
                params=data.get("params", {}).copy(),
                metadata=Metadata.from_dict(data["metadata"]),
                raw_content=data.get("raw_content", "")
            )

            # Add sections
            for section_data in data.get("sections", []):
                section = Section.from_dict(section_data)
                container.add_section(section)

            return container

        except Exception as e:
            logger.error(f"Failed to create container from dict: {str(e)}")
            raise
