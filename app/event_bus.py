"""
EventBus module for TypeMaster decoupled event propagation.
"""
import logging
from typing import Callable, Dict, List

logger = logging.getLogger("app.event_bus")

class EventBus:
    """
    Centralized event bus to allow lightweight, publisher-subscriber communication
    between the engine states and UI components, decoupling direct class references.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Subscribes a callback to an event type.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)
            logger.debug(f"Subscribed callback {callback.__name__ if hasattr(callback, '__name__') else callback} to event: {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """
        Unsubscribes a callback from an event type.
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
                logger.debug(f"Unsubscribed callback {callback.__name__ if hasattr(callback, '__name__') else callback} from event: {event_type}")
            except ValueError:
                pass

    def publish(self, event_type: str, *args, **kwargs) -> None:
        """
        Publishes an event to all subscribed callbacks.
        """
        if event_type not in self._subscribers:
            return
        
        # Make a copy in case a callback unsubscribes itself during publication
        callbacks = list(self._subscribers[event_type])
        for callback in callbacks:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing callback in EventBus for event '{event_type}': {e}", exc_info=True)
