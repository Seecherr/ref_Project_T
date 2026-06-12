"""Unit tests for NotificationService and BookAvailabilityListener."""

from src.models.reservation import Reservation
from src.services.notification_service import BookAvailabilityListener
from src.utils.event_manager import Event, EventManager


class TestNotificationService:
    """Tests for NotificationService."""

    def test_send_notification(self, notification_service):
        n = notification_service.send_notification("M1", "Hello")
        assert n.member_id == "M1"
        assert n.message == "Hello"
        assert n.is_read is False

    def test_mark_as_read(self, notification_service):
        n = notification_service.send_notification("M1", "Hello")
        result = notification_service.mark_as_read(n.notification_id)
        assert result.is_read is True

    def test_mark_as_read_nonexistent(self, notification_service):
        assert notification_service.mark_as_read("nonexistent") is None

    def test_mark_as_unread(self, notification_service):
        n = notification_service.send_notification("M1", "Hello")
        notification_service.mark_as_read(n.notification_id)
        result = notification_service.mark_as_unread(n.notification_id)
        assert result.is_read is False

    def test_mark_as_unread_nonexistent(self, notification_service):
        assert notification_service.mark_as_unread("nonexistent") is None

    def test_get_notifications(self, notification_service):
        notification_service.send_notification("M1", "A")
        notification_service.send_notification("M1", "B")
        notification_service.send_notification("M2", "C")
        results = notification_service.get_notifications("M1")
        assert len(results) == 2

    def test_get_unread_notifications(self, notification_service):
        n1 = notification_service.send_notification("M1", "A")
        notification_service.send_notification("M1", "B")
        notification_service.mark_as_read(n1.notification_id)
        unread = notification_service.get_unread_notifications("M1")
        assert len(unread) == 1

    def test_get_notification(self, notification_service):
        n = notification_service.send_notification("M1", "Hello")
        result = notification_service.get_notification(n.notification_id)
        assert result is n

    def test_get_notification_nonexistent(self, notification_service):
        assert notification_service.get_notification("nonexistent") is None

    def test_get_all_notifications(self, notification_service):
        notification_service.send_notification("M1", "A")
        notification_service.send_notification("M2", "B")
        assert len(notification_service.get_all_notifications()) == 2


class TestBookAvailabilityListener:
    """Tests for BookAvailabilityListener."""

    def test_book_returned_event(self, notification_service):
        from src.storage.in_memory_reservation_repository import InMemoryReservationRepository

        reservation_repo = InMemoryReservationRepository()
        reservation_repo.add(Reservation(reservation_id="R1", member_id="M1", book_isbn="978-1"))

        listener = BookAvailabilityListener(notification_service, reservation_repo)
        listener.update(Event.BOOK_RETURNED, {"isbn": "978-1"})

        notifications = notification_service.get_notifications("M1")
        assert len(notifications) == 1
        assert "978-1" in notifications[0].message

    def test_reservation_fulfilled_event(self, notification_service):
        listener = BookAvailabilityListener(notification_service)
        listener.update(Event.RESERVATION_FULFILLED, {"member_id": "M1", "book_isbn": "978-1"})

        notifications = notification_service.get_notifications("M1")
        assert len(notifications) == 1
        assert "fulfilled" in notifications[0].message.lower()

    def test_member_blocked_event(self, notification_service):
        listener = BookAvailabilityListener(notification_service)
        listener.update(Event.MEMBER_BLOCKED, {"member_id": "M1", "total_fines": "30.00"})

        notifications = notification_service.get_notifications("M1")
        assert len(notifications) == 1
        assert "blocked" in notifications[0].message.lower()

    def test_member_unblocked_event(self, notification_service):
        listener = BookAvailabilityListener(notification_service)
        listener.update(Event.MEMBER_UNBLOCKED, {"member_id": "M1"})

        notifications = notification_service.get_notifications("M1")
        assert len(notifications) == 1
        assert "unblocked" in notifications[0].message.lower()

    def test_book_returned_no_reservations(self, notification_service):
        from src.storage.in_memory_reservation_repository import InMemoryReservationRepository

        reservation_repo = InMemoryReservationRepository()
        listener = BookAvailabilityListener(notification_service, reservation_repo)
        listener.update(Event.BOOK_RETURNED, {"isbn": "978-1"})
        assert len(notification_service.get_all_notifications()) == 0

    def test_integration_with_event_manager(self, notification_service):
        em = EventManager()
        listener = BookAvailabilityListener(notification_service)
        em.subscribe(Event.MEMBER_BLOCKED, listener)
        em.notify(Event.MEMBER_BLOCKED, {"member_id": "M1", "total_fines": "50.00"})
        notifications = notification_service.get_notifications("M1")
        assert len(notifications) == 1
