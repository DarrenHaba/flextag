from typing import Protocol

from .container import IContainer


class ITransportContainer(Protocol):
    """Interface for transport container format"""

    def encode(self, container: IContainer) -> str:
        """Convert data container to transport format"""
        ...

    @classmethod
    def decode(cls, data: str) -> IContainer:
        """Convert transport format to data container"""
        ...
