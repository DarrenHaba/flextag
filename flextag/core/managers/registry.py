from typing import Dict, Any, List
from flextag.core.interfaces.managers import IRegistryManager
from flextag.logger import logger
from flextag.exceptions import FlexTagError


class RegistryManager(IRegistryManager):
    """Central registry manager for all components"""

    def __init__(self):
        self._registries: Dict[str, Dict[str, Any]] = {}
        logger.debug("Initialized RegistryManager")

    def create_registry(self, name: str) -> None:
        """Create a new component registry"""
        if name in self._registries:
            raise FlexTagError(f"Registry '{name}' already exists")
        self._registries[name] = {}
        logger.debug(f"Created registry: {name}")

    def get_registry(self, name: str) -> Dict[str, Any]:
        """Get registry by name"""
        if name not in self._registries:
            raise FlexTagError(f"Registry '{name}' not found")
        return self._registries[name]

    def register(self, registry: str, name: str, implementation: Any) -> None:
        """Register implementation in specific registry"""
        try:
            if registry not in self._registries:
                self.create_registry(registry)

            self._registries[registry][name] = implementation
            logger.debug(
                f"Registered implementation '{name}' in registry '{registry}'"
            )

        except Exception as e:
            logger.error(
                f"Failed to register implementation: {str(e)}",
                registry=registry,
                name=name
            )
            raise FlexTagError(
                f"Failed to register '{name}' in '{registry}': {str(e)}"
            )

    def unregister(self, registry: str, name: str) -> None:
        """Remove implementation from registry"""
        try:
            if registry not in self._registries:
                raise FlexTagError(f"Registry '{registry}' not found")

            if name not in self._registries[registry]:
                raise FlexTagError(
                    f"Implementation '{name}' not found in registry '{registry}'"
                )

            del self._registries[registry][name]
            logger.debug(
                f"Unregistered implementation '{name}' from registry '{registry}'"
            )

        except Exception as e:
            logger.error(
                f"Failed to unregister implementation: {str(e)}",
                registry=registry,
                name=name
            )
            raise

    def get(self, registry: str, name: str) -> Any:
        """Get implementation from registry"""
        try:
            if registry not in self._registries:
                raise FlexTagError(f"Registry '{registry}' not found")

            if name not in self._registries[registry]:
                raise FlexTagError(
                    f"Implementation '{name}' not found in registry '{registry}'"
                )

            return self._registries[registry][name]

        except Exception as e:
            logger.error(
                f"Failed to get implementation: {str(e)}",
                registry=registry,
                name=name
            )
            raise

    def list_registries(self) -> List[str]:
        """List all available registries"""
        return list(self._registries.keys())

    def list_registered(self, registry: str) -> List[str]:
        """List all implementations in a registry"""
        if registry not in self._registries:
            raise FlexTagError(f"Registry '{registry}' not found")
        return list(self._registries[registry].keys())
