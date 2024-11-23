from typing import Any, Dict, Type
import json
import yaml

from .container import Container
from ..base.parser import BaseFlexTagParser
from ..interfaces.parser import IContentParser
from ...exceptions import ContainerError
from ...logger import logger


class ContentParser(IContentParser):
    """Base content format parser"""

    def parse(self, content: str) -> Any:
        return content  # Pass through for text

    def dump(self, data: Any) -> str:
        return str(data)  # Convert to string for text


class JSONParser(IContentParser):
    """JSON format parser"""

    def parse(self, content: str) -> Dict:
        if not content.strip():
            return {}
        return json.loads(content)

    def dump(self, data: Any) -> str:
        return json.dumps(data, indent=2)


class YAMLParser(IContentParser):
    """YAML format parser"""

    def parse(self, content: str) -> Dict:
        if not content.strip():
            return {}
        return yaml.safe_load(content)

    def dump(self, data: Any) -> str:
        return yaml.safe_dump(data, sort_keys=False)


class FlexTagParser(BaseFlexTagParser):
    """Concrete implementation of FlexTag parser"""

    def __init__(self):
        super().__init__()
        # Register parser instances (not classes)
        self.register_content_parser("text", ContentParser())
        self.register_content_parser("json", JSONParser())
        self.register_content_parser("yaml", YAMLParser())
        logger.debug("Initialized FlexTag parser with default content parsers")

    def parse(self, content: str) -> Container:
        """Parse string content to Container"""
        try:
            # Create container from string content
            container = Container.from_string(content)

            # Parse section contents based on format
            for section in container.sections:
                fmt = section.parameters.get("fmt", "text")
                try:
                    parser = self.get_content_parser(fmt)
                    if parser:
                        section.content = parser.parse(section.content)
                except Exception as e:
                    logger.warning(
                        f"Failed to parse section content: {str(e)}",
                        section_id=section.id,
                        fmt=fmt,
                    )

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
                fmt = section.parameters.get("fmt", "text")
                try:
                    parser = self.get_content_parser(fmt)
                    # Create new section with dumped content
                    new_section = section.__class__(
                        **{
                            "id": section.id,
                            "tags": section.tags.copy(),
                            "paths": section.paths.copy(),
                            "parameters": section.parameters.copy(),
                            "content": parser.dump(section.content),
                            "fmt": section.fmt,
                            "enc": section.enc,
                            "crypt": section.crypt,
                            "comp": section.comp,
                            "lang": section.lang,
                        }
                    )
                    doc.sections.append(new_section)
                except Exception as e:
                    logger.error(
                        f"Failed to dump section content: {str(e)}",
                        section_id=section.id,
                        fmt=fmt,
                    )
                    raise ContainerError(
                        f"Failed to serialize content for section '{section.id}' "
                        f"with format '{fmt}': {str(e)}"
                    )

            return doc.to_string()

        except ContainerError:
            raise
        except Exception as e:
            logger.error(f"Container serialization error: {str(e)}")
            raise ContainerError(f"Failed to serialize container: {str(e)}")
