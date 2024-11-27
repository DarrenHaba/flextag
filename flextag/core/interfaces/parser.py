from typing import Protocol, Any, Dict
from flextag.core.types.container import Container
from flextag.core.types.section import Section
from flextag.core.types.metadata import Metadata


class IContentParser(Protocol):
    """Parser for specific content formats (json, yaml, text, etc)"""

    def parse(self, content: str) -> Any:
        """Parse content string into native format"""
        ...

    def dump(self, data: Any) -> str:
        """Convert native format back to string"""
        ...


class IMetadataParser(Protocol):
    """Parser for metadata headers"""

    def parse_params(self, header: str) -> Dict[str, Any]:
        """Parse [[PARAMS]] header"""
        ...

    def parse_meta(self, header: str) -> Metadata:
        """Parse [[META]] header"""
        ...

    def parse_section_meta(self, header: str) -> Metadata:
        """Parse [[SEC]] header metadata"""
        ...


class ISectionParser(Protocol):
    """Parser for complete sections"""

    def parse(self, raw_section: str, content_parser: IContentParser) -> Section:
        """Parse raw section text into Section object"""
        ...

    def dump(self, section: Section, content_parser: IContentParser) -> str:
        """Convert section back to string format"""
        ...


class IContainerParser(Protocol):
    """Parser for complete containers"""

    def parse(self, content: str) -> Container:
        """Parse raw content into Container object"""
        ...

    def dump(self, container: Container) -> str:
        """Convert container back to string format"""
        ...
