"""Unit tests for EventManager (Observer Pattern)."""

from typing import Any

from src.utils.event_manager import Event, EventListener, EventManager


class MockListener(EventListener):
    """Mock listener for testing."""

    def __init__(self):
        self.events_received: list[tuple[Event, dict]] = []

    def update(self, event: Event, data: dict[str, Any]) -> None:
        self.events_received.append((event, data))


class TestEvent:
    """Tests for Event enum."""

    def test_book_returned(self):
        assert Event.BOOK_RETURNED.value == "book_returned"

    def test_book_available(self):
        assert Event.BOOK_AVAILABLE.value == "book_available"

    def test_member_blocked(self):
        assert Event.MEMBER_BLOCKED.value == "member_blocked"

    def test_fine_created(self):
        assert Event.FINE_CREATED.value == "fine_created"

    def test_reservation_fulfilled(self):
        assert Event.RESERVATION_FULFILLED.value == "reservation_fulfilled"


class TestEventManager:
    """Tests for EventManager."""

    def test_subscribe_and_notify(self):
        em = EventManager()
        listener = MockListener()
        em.subscribe(Event.BOOK_RETURNED, listener)
        em.notify(Event.BOOK_RETURNED, {"isbn": "978-1"})
        assert len(listener.events_received) == 1
        assert listener.events_received[0][0] == Event.BOOK_RETURNED
        assert listener.events_received[0][1]["isbn"] == "978-1"

    def test_notify_no_listeners(self):
        em = EventManager()
        em.notify(Event.BOOK_RETURNED, {"isbn": "978-1"})  # Should not raise

    def test_multiple_listeners(self):
        em = EventManager()
        l1 = MockListener()
        l2 = MockListener()
        em.subscribe(Event.BOOK_RETURNED, l1)
        em.subscribe(Event.BOOK_RETURNED, l2)
        em.notify(Event.BOOK_RETURNED, {"isbn": "978-1"})
        assert len(l1.events_received) == 1
        assert len(l2.events_received) == 1

    def test_unsubscribe(self):
        em = EventManager()
        listener = MockListener()
        em.subscribe(Event.BOOK_RETURNED, listener)
        em.unsubscribe(Event.BOOK_RETURNED, listener)
        em.notify(Event.BOOK_RETURNED, {"isbn": "978-1"})
        assert len(listener.events_received) == 0

    def test_unsubscribe_nonexistent(self):
        em = EventManager()
        listener = MockListener()
        em.unsubscribe(Event.BOOK_RETURNED, listener)  # Should not raise

    def test_subscribe_different_events(self):
        em = EventManager()
        l1 = MockListener()
        l2 = MockListener()
        em.subscribe(Event.BOOK_RETURNED, l1)
        em.subscribe(Event.FINE_CREATED, l2)
        em.notify(Event.BOOK_RETURNED, {})
        assert len(l1.events_received) == 1
        assert len(l2.events_received) == 0

    def test_get_listeners(self):
        em = EventManager()
        l1 = MockListener()
        l2 = MockListener()
        em.subscribe(Event.BOOK_RETURNED, l1)
        em.subscribe(Event.BOOK_RETURNED, l2)
        listeners = em.get_listeners(Event.BOOK_RETURNED)
        assert len(listeners) == 2

    def test_get_listeners_empty(self):
        em = EventManager()
        assert em.get_listeners(Event.BOOK_RETURNED) == []

    def test_clear_specific_event(self):
        em = EventManager()
        l1 = MockListener()
        l2 = MockListener()
        em.subscribe(Event.BOOK_RETURNED, l1)
        em.subscribe(Event.FINE_CREATED, l2)
        em.clear(Event.BOOK_RETURNED)
        assert em.get_listeners(Event.BOOK_RETURNED) == []
        assert len(em.get_listeners(Event.FINE_CREATED)) == 1

    def test_clear_all(self):
        em = EventManager()
        em.subscribe(Event.BOOK_RETURNED, MockListener())
        em.subscribe(Event.FINE_CREATED, MockListener())
        em.clear()
        assert em.get_listeners(Event.BOOK_RETURNED) == []
        assert em.get_listeners(Event.FINE_CREATED) == []

    def test_duplicate_subscribe(self):
        em = EventManager()
        listener = MockListener()
        em.subscribe(Event.BOOK_RETURNED, listener)
        em.subscribe(Event.BOOK_RETURNED, listener)  # Should not add duplicate
        assert len(em.get_listeners(Event.BOOK_RETURNED)) == 1

    def test_notify_with_none_data(self):
        em = EventManager()
        listener = MockListener()
        em.subscribe(Event.BOOK_RETURNED, listener)
        em.notify(Event.BOOK_RETURNED)
        assert listener.events_received[0][1] == {}
