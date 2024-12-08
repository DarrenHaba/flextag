from typing import Dict, List, Any, Callable
import weakref
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dataclass
class ManagerEvent:
    """Event data structure for manager communications"""
    source: str          # Source manager name
    event_type: str      # Event type
    data: Any           # Event payload


class BaseManager:
    """Base manager with event and registry capabilities"""

    def __init__(self, name: str):
        self.name = name
        self._listeners: Dict[str, List[weakref.ref[Callable]]] = {}
        self._connected_managers: Dict[str, 'BaseManager'] = {}
        self._registries: Dict[str, Dict[str, Any]] = {}
        self._event_handlers = []  # Keep strong references
        logger.debug(f"Initialized {name}")

    def register(self, registry: str, name: str, implementation: Any) -> None:
        """Register implementation in registry"""
        if registry not in self._registries:
            self._registries[registry] = {}

        self._registries[registry][name] = implementation
        logger.debug(f"{self.name}: Registered '{name}' in '{registry}'")

    def get(self, registry: str, name: str) -> Any:
        """Get implementation from registry"""
        if registry not in self._registries:
            raise ValueError(f"Registry '{registry}' not found")

        if name not in self._registries[registry]:
            raise ValueError(f"Implementation '{name}' not found in '{registry}'")

        return self._registries[registry][name]

    def subscribe(self, event_type: str, callback: Callable[[ManagerEvent], None]) -> None:
        """Subscribe to event type"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._event_handlers.append(callback)  # Keep strong reference
        self._listeners[event_type].append(weakref.ref(callback))
        logger.debug(f"{self.name}: Subscribed to {event_type}")

    def emit(self, event_type: str, data: Any = None) -> None:
        """Emit event to all listeners including connected managers"""
        event = ManagerEvent(self.name, event_type, data)
        logger.debug(f"{self.name}: Emitting event {event_type}")

        # Local listeners
        if event_type in self._listeners:
            logger.debug(f"{self.name}: Found {len(self._listeners[event_type])} local listeners")
            for cb_ref in self._listeners[event_type]:
                callback = cb_ref()
                if callback is not None:
                    try:
                        logger.debug(f"{self.name}: Calling local handler for {event_type}")
                        callback(event)
                    except Exception as e:
                        logger.error(f"Error in event handler: {str(e)}")
                else:
                    logger.debug(f"{self.name}: Dead reference found for {event_type}")

        # Connected managers
        logger.debug(f"{self.name}: Found {len(self._connected_managers)} connected managers")
        for manager in self._connected_managers.values():
            try:
                logger.debug(f"{self.name}: Propagating {event_type} to {manager.name}")
                manager._handle_event(event)
            except Exception as e:
                logger.error(f"Error propagating event to {manager.name}: {str(e)}")

    def connect(self, manager: 'BaseManager') -> None:
        """Connect to another manager"""
        self._connected_managers[manager.name] = manager
        logger.debug(f"{self.name}: Connected to {manager.name}")

    def _handle_event(self, event: ManagerEvent) -> None:
        """Handle incoming event from connected manager"""
        logger.debug(f"{self.name}: Handling {event.event_type} from {event.source}")

        if event.event_type in self._listeners:
            logger.debug(f"{self.name}: Found {len(self._listeners[event.event_type])} handlers")
            for cb_ref in self._listeners[event.event_type]:
                callback = cb_ref()
                if callback is not None:
                    try:
                        logger.debug(f"{self.name}: Executing handler for {event.event_type}")
                        callback(event)
                    except Exception as e:
                        logger.error(f"Error in event handler: {str(e)}")
                else:
                    logger.debug(f"{self.name}: Dead reference found for {event.event_type}")

    def create_registry(self, name: str) -> None:
        """Create a new registry"""
        if name in self._registries:
            logger.warning(f"Registry '{name}' already exists")
            return
        self._registries[name] = {}
        logger.debug(f"{self.name}: Created registry '{name}'")
