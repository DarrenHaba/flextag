from typing import Dict, Optional
from flextag.core.interfaces.managers import IParserManager
from flextag.core.interfaces.parser import (
    IContainerParser,
    ISectionParser,
    IContentParser
)
from flextag.core.types.container import Container
from flextag.core.types.section import Section
from flextag.logger import logger
from flextag.exceptions import FlexTagError


class ParserManager(IParserManager):
    """Manager for parsing operations"""

    def __init__(self):
        # Parser instances
        self._container_parser: Optional[IContainerParser] = None
        self._section_parser: Optional[ISectionParser] = None
        self._content_parsers: Dict[str, IContentParser] = {}

        logger.debug("Initialized ParserManager")

    def register_container_parser(self, parser: IContainerParser) -> None:
        """Register container parser implementation"""
        self._container_parser = parser
        logger.debug("Registered container parser")

    def register_section_parser(self, parser: ISectionParser) -> None:
        """Register section parser implementation"""
        self._section_parser = parser
        logger.debug("Registered section parser")

    def register_content_parser(self, fmt: str, parser: IContentParser) -> None:
        """Register content parser for specific format"""
        self._content_parsers[fmt] = parser
        logger.debug(f"Registered content parser for format: {fmt}")

    def get_content_parser(self, fmt: str) -> IContentParser:
        """Get parser for specific content format"""
        if fmt not in self._content_parsers:
            raise FlexTagError(f"No parser registered for format: {fmt}")
        return self._content_parsers[fmt]

    def parse_container(self, content: str) -> Container:
        """Parse raw content into container"""
        try:
            if not self._container_parser:
                raise FlexTagError("No container parser registered")

            container = self._container_parser.parse(content)
            logger.debug(
                f"Parsed container with {len(container.sections)} sections"
            )
            return container

        except Exception as e:
            logger.error(f"Container parsing failed: {str(e)}")
            raise

    def parse_section(self, content: str, fmt: str = "text") -> Section:
        """Parse raw content into section"""
        try:
            if not self._section_parser:
                raise FlexTagError("No section parser registered")

            content_parser = self.get_content_parser(fmt)
            section = self._section_parser.parse(content, content_parser)

            logger.debug(
                f"Parsed section: id={section.metadata.id}, "
                f"format={fmt}"
            )
            return section

        except Exception as e:
            logger.error(f"Section parsing failed: {str(e)}")
            raise

    def dump_container(self, container: Container) -> str:
        """Convert container to string format"""
        try:
            if not self._container_parser:
                raise FlexTagError("No container parser registered")

            result = self._container_parser.dump(container)
            logger.debug("Dumped container to string format")
            return result

        except Exception as e:
            logger.error(f"Container dumping failed: {str(e)}")
            raise

    def dump_section(self, section: Section) -> str:
        """Convert section to string format"""
        try:
            if not self._section_parser:
                raise FlexTagError("No section parser registered")

            fmt = section.metadata.fmt
            content_parser = self.get_content_parser(fmt)

            result = self._section_parser.dump(section, content_parser)
            logger.debug(f"Dumped section: id={section.metadata.id}")
            return result

        except Exception as e:
            logger.error(f"Section dumping failed: {str(e)}")
            raise
