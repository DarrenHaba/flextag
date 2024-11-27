from typing import Protocol, Any, List


class IRegistry(Protocol):
    """Interface for component registries"""

    def register(self, name: str, implementation: Any) -> None:
        """Register an implementation under a name"""
        ...

    def unregister(self, name: str) -> None:
        """Remove a registered implementation"""
        ...

    def get(self, name: str) -> Any:
        """Get implementation by name"""
        ...

    def list_registered(self) -> List[str]:
        """List all registered implementation names"""
        ...
