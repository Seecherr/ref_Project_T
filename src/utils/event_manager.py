"""Observer Pattern: Event management system.

Implements the Observer GoF pattern to provide loose coupling
between components. Services publish events, and listeners
react to them without direct dependencies.

Events:
    - BOOK_RETURNED: Fired when a book is returned.
    - BOOK_AVAILABLE: Fired when a book becomes available.
    - MEMBER_BLOCKED: Fired when a member is blocked.
    - MEMBER_UNBLOCKED: Fired when a member is unblocked.
    - FINE_CREATED: Fired when a new fine is created.
    - RESERVATION_FULFILLED: Fired when a reservation is fulfilled.
"""

from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from typing import Any


class Event(enum.Enum):
    """Events that can be published through the EventManager."""

    BOOK_RETURNED = "book_returned"
    BOOK_AVAILABLE = "book_available"
    MEMBER_BLOCKED = "member_blocked"
    MEMBER_UNBLOCKED = "member_unblocked"
    FINE_CREATED = "fine_created"
    RESERVATION_FULFILLED = "reservation_fulfilled"


class EventListener(ABC):
    """Abstract listener that reacts to published events.

    Concrete listeners implement the update method to handle
    specific events they are subscribed to.
    """

    @abstractmethod
    def update(self, event: Event, data: dict[str, Any]) -> None:
        """Handle a published event.

        Args:
            event: The event type that was published.
            data: Event-specific data payload.
        """
        ...  # pragma: no cover


class EventManager:
    """Central event manager that connects publishers and listeners.

    Manages subscriptions and dispatches events to registered listeners.
    Follows the Mediator aspect of the Observer pattern.
    """

    def __init__(self) -> None:
        """Initialize the event manager with empty subscription lists."""
        self._listeners: dict[Event, list[EventListener]] = {}

    def subscribe(self, event: Event, listener: EventListener) -> None:
        """Subscribe a listener to an event.

        Args:
            event: The event type to listen for.
            listener: The listener to notify when the event occurs.
        """
        if event not in self._listeners:
            self._listeners[event] = []
        if listener not in self._listeners[event]:
            self._listeners[event].append(listener)

    def unsubscribe(self, event: Event, listener: EventListener) -> None:
        """Unsubscribe a listener from an event.

        Args:
            event: The event type to stop listening for.
            listener: The listener to remove.
        """
        if event in self._listeners:
            self._listeners[event] = [existing for existing in self._listeners[event] if existing is not listener]

    def notify(self, event: Event, data: dict[str, Any] | None = None) -> None:
        """Publish an event to all subscribed listeners.

        Args:
            event: The event type to publish.
            data: Optional event-specific data payload.
        """
        if data is None:
            data = {}
        for listener in self._listeners.get(event, []):
            listener.update(event, data)

    def get_listeners(self, event: Event) -> list[EventListener]:
        """Get all listeners subscribed to an event.

        Args:
            event: The event type.

        Returns:
            List of listeners subscribed to the event.
        """
        return list(self._listeners.get(event, []))

    def clear(self, event: Event | None = None) -> None:
        """Clear listeners for a specific event, or all events.

        Args:
            event: The specific event to clear. If None, clears all.
        """
        if event is None:
            self._listeners.clear()
        elif event in self._listeners:
            self._listeners[event] = []
