from typing import Any, Dict, Type
import json
import yaml
import gzip
import zipfile
from io import StringIO
from ..base.parser import BaseFlexTagParser
from ..interfaces.parser import IContentParser
from flextag.exceptions import ContainerError
from flextag.logger import logger


class ContentParser:
    """Base content format parser"""
    def parse(self, content: str) -> Any:
        raise NotImplementedError

    def dump(self, data: Any) -> str:
        raise NotImplementedError


class JSONParser(ContentParser):
    """JSON format parser"""
    def parse(self, content: str) -> Dict:
        return json.loads(content)

    def dump(self, data: Any) -> str:
        return json.dumps(data, indent=2)


class YAMLParser(ContentParser):
    """YAML format parser"""
    def parse(self, content: str) -> Dict:
        return yaml.safe_load(content)

    def dump(self, data: Any) -> str:
        return yaml.safe_dump(data, sort_keys=False)

class FlexTagParser(BaseFlexTagParser):
    """Concrete implementation of FlexTag parser"""

    def __init__(self):
        super().__init__()
        # Register default parsers
        self.register_content_parser("json", JSONParser)
        self.register_content_parser("yaml", YAMLParser)
        self.register_content_parser("text", ContentParser)  # Passthrough for text
        logger.debug("Initialized FlexTag parser with default content parsers")

    def parse(self, content: str) -> "Container":
        """Parse string content to Container"""
        try:
            from .container import Container  # Import here to avoid circular dependency
            container = Container.from_string(content)

            # Parse section contents based on format
            for section in container.sections:
                if section.fmt in self.content_parsers:
                    parser = self.get_content_parser(section.fmt)
                    try:
                        section.content = parser.parse(section.content)
                    except Exception as e:
                        logger.warning(f"Failed to parse section content: {str(e)}",
                                       section_id=section.id, fmt=section.fmt)

            return container

        except Exception as e:
            logger.error(f"Container parsing error: {str(e)}")
            raise ContainerError(f"Failed to parse container: {str(e)}")

    def dump(self, container: "Container") -> str:
        """Convert container to string format"""
        try:
            # Create a copy to avoid modifying the original
            from .container import Container
            doc = Container()
            doc.metadata = container.metadata.copy()
            doc.params = container.params.copy()

            # Process sections
            for section in container.sections:
                if section.fmt in self.content_parsers:
                    parser = self.get_content_parser(section.fmt)
                    try:
                        section.content = parser.dump(section.content)
                    except Exception as e:
                        logger.warning(f"Failed to dump section content: {str(e)}",
                                       section_id=section.id, fmt=section.fmt)
                doc.sections.append(section)

            return doc.to_string()

        except Exception as e:
            logger.error(f"Container serialization error: {str(e)}")
            raise ContainerError(f"Failed to serialize container: {str(e)}")
