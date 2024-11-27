from typing import Protocol, List, Optional, Dict, Any
from flextag.core.types.container import Container
from flextag.core.types.section import Section
from flextag.core.interfaces.parser import IContentParser, IContainerParser, ISectionParser
from flextag.core.interfaces.search import ISearchAlgorithm
from flextag.core.interfaces.transport import ICompressor, IEncoder


class IParserManager(Protocol):
    """Manager for parsing operations"""

    def register_container_parser(self, parser: IContainerParser) -> None:
        """Register container parser implementation"""
        ...

    def register_section_parser(self, parser: ISectionParser) -> None:
        """Register section parser implementation"""
        ...

    def register_content_parser(self, fmt: str, parser: IContentParser) -> None:
        """Register content parser for specific format"""
        ...

    def get_content_parser(self, fmt: str) -> IContentParser:
        """Get parser for specific content format"""
        ...

    def parse_container(self, content: str) -> Container:
        """Parse raw content into container"""
        ...

    def parse_section(self, content: str, fmt: str = "text") -> Section:
        """Parse raw content into section"""
        ...

    def dump_container(self, container: Container) -> str:
        """Convert container to string format"""
        ...

    def dump_section(self, section: Section) -> str:
        """Convert section to string format"""
        ...


class ISearchManager(Protocol):
    """Manager for search operations"""

    def register_algorithm(self, name: str, algorithm: ISearchAlgorithm) -> None:
        """Register search algorithm implementation"""
        ...

    def set_active_algorithm(self, name: str) -> None:
        """Set active search algorithm"""
        ...

    def auto_select_algorithm(self, query: str) -> None:
        """Auto-select appropriate algorithm based on query complexity"""
        ...

    def filter(self, containers: List[Container], query: str) -> List[Container]:
        """Filter containers based on metadata query"""
        ...

    def find(self, container: Container, query: str) -> List[Section]:
        """Find all matching sections"""
        ...

    def find_first(self, container: Container, query: str) -> Optional[Section]:
        """Find first matching section"""
        ...


class ITransportManager(Protocol):
    """Manager for transport operations"""

    def register_compressor(self, name: str, compressor: ICompressor) -> None:
        """Register compression implementation"""
        ...

    def register_encoder(self, name: str, encoder: IEncoder) -> None:
        """Register encoder implementation"""
        ...

    def set_default_encoding(self, encoding: str) -> None:
        """Set default encoding type (base64, base32, base16)"""
        ...

    def set_default_compression(self, compression: str) -> None:
        """Set default compression algorithm"""
        ...

    def to_transport(self,
                     container: Container,
                     encoding: Optional[str] = None,
                     compression: Optional[str] = None) -> str:
        """Convert container to transport format"""
        ...

    def from_transport(self, transport: str) -> Container:
        """Convert transport format back to container"""
        ...


class IRegistryManager(Protocol):
    """Manager for component registries"""

    def create_registry(self, name: str) -> None:
        """Create a new component registry"""
        ...

    def get_registry(self, name: str) -> Dict[str, Any]:
        """Get registry by name"""
        ...

    def register(self, registry: str, name: str, implementation: Any) -> None:
        """Register implementation in specific registry"""
        ...

    def unregister(self, registry: str, name: str) -> None:
        """Remove implementation from registry"""
        ...

    def get(self, registry: str, name: str) -> Any:
        """Get implementation from registry"""
        ...

    def list_registries(self) -> List[str]:
        """List all available registries"""
        ...

    def list_registered(self, registry: str) -> List[str]:
        """List all implementations in a registry"""
        ...
