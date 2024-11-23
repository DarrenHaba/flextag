from typing import Optional, List

from .interfaces.container import IContainer
from .interfaces.section import ISection


class ContainerManager:
    """Manages multiple FlexTag containers"""

    def __init__(self, containers: List[IContainer] = None):
        self.containers = containers or []

    def filter(self, query: str) -> "ContainerManager":
        """Filter containers by metadata"""
        matching = []
        for container in self.containers:
            matching.extend(container.filter(query))
        return ContainerManager(matching)

    def search(self, query: str) -> List[ISection]:
        """Search sections across all containers"""
        results = []
        for container in self.containers:
            results.extend(container.search(query))
        return results

    def find_first(self, query: str) -> Optional[ISection]:
        """Find first matching section across all containers"""
        for container in self.containers:
            if result := container.find_first(query):
                return result
        return None
