from abc import ABC
from typing import Dict, List, Any, Optional
from ..interfaces.container import IContainer
from ..interfaces.section import ISection
from flextag.exceptions import SearchError
from flextag.logger import logger
from flextag.settings import Const


class BaseContainer(ABC, IContainer):
    """Base implementation of IContainer with common functionality"""

    def __init__(self):
        self.metadata: Dict[str, Any] = {}
        self.params: Dict[str, Any] = Const.DEFAULTS.copy()
        self.sections: List[ISection] = []
        logger.debug("Initialized new container")

    def add_section(self, section: ISection) -> None:
        """Add a section with parameter inheritance"""
        # Apply container params as defaults
        for key, value in self.params.items():
            if key not in section.parameters:
                section.parameters[key] = value

        self.sections.append(section)
        logger.debug(f"Added section {section.id} to container")

    def find_first(self, query: str) -> Optional[ISection]:
        """Find first section matching query"""
        try:
            for section in self.sections:
                if section.matches(query):
                    return section
            return None
        except Exception as e:
            logger.error(f"Error in find_first: {str(e)}", query=query)
            raise SearchError(f"Invalid query syntax: {query}")

    def search(self, query: str) -> List[ISection]:
        """Find all sections matching query"""
        try:
            return [s for s in self.sections if s.matches(query)]
        except Exception as e:
            logger.error(f"Error in search: {str(e)}", query=query)
            raise SearchError(f"Invalid query syntax: {query}")
