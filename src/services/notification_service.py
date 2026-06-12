"""Notification management service for the Library Management System.

Handles sending notifications, marking as read, and retrieving
notifications for members. Integrates with the Observer pattern.
"""

from __future__ import annotations

from typing import Any

from src.models.notification import Notification
from src.storage.interfaces import NotificationRepository
from src.utils.event_manager import Event, EventListener
from src.utils.id_generator import generate_id


class NotificationService:
    """Service for managing member notifications.

    Provides operations for sending, reading, and querying notifications.
    """

    def __init__(
        self,
        notification_repo: NotificationRepository,
    ) -> None:
        """Initialize with repository dependency.

        Args:
            notification_repo: Repository for Notification entities.
        """
        self._notification_repo = notification_repo

    def send_notification(
        self,
        member_id: str,
        message: str,
    ) -> Notification:
        """Send a notification to a member.

        Args:
            member_id: The recipient member ID.
            message: The notification message.

        Returns:
            The created Notification.
        """
        notification = Notification(
            notification_id=generate_id(),
            member_id=member_id,
            message=message,
        )
        self._notification_repo.add(notification)
        return notification

    def mark_as_read(self, notification_id: str) -> Notification | None:
        """Mark a notification as read.

        Args:
            notification_id: The notification to mark.

        Returns:
            The updated Notification, or None if not found.
        """
        notification = self._notification_repo.get_by_id(notification_id)
        if not notification:
            return None
        notification.mark_read()
        self._notification_repo.update(notification)
        return notification

    def mark_as_unread(self, notification_id: str) -> Notification | None:
        """Mark a notification as unread.

        Args:
            notification_id: The notification to mark.

        Returns:
            The updated Notification, or None if not found.
        """
        notification = self._notification_repo.get_by_id(notification_id)
        if not notification:
            return None
        notification.mark_unread()
        self._notification_repo.update(notification)
        return notification

    def get_notifications(self, member_id: str) -> list[Notification]:
        """Get all notifications for a member.

        Args:
            member_id: The member whose notifications to retrieve.

        Returns:
            List of notifications, newest first.
        """
        return self._notification_repo.get_by_member(member_id)

    def get_unread_notifications(self, member_id: str) -> list[Notification]:
        """Get unread notifications for a member.

        Args:
            member_id: The member whose unread notifications to retrieve.

        Returns:
            List of unread notifications, newest first.
        """
        return self._notification_repo.get_unread_by_member(member_id)

    def get_notification(self, notification_id: str) -> Notification | None:
        """Get a notification by ID.

        Args:
            notification_id: The notification to retrieve.

        Returns:
            The Notification, or None if not found.
        """
        return self._notification_repo.get_by_id(notification_id)

    def get_all_notifications(self) -> list[Notification]:
        """Get all notifications.

        Returns:
            List of all notifications.
        """
        return self._notification_repo.get_all()


class BookAvailabilityListener(EventListener):
    """Observer that listens for book returns and notifies waiting readers.

    This is the concrete Observer in the Observer pattern. It listens
    for BOOK_RETURNED events and sends notifications to members
    who have reservations for the returned book.
    """

    def __init__(
        self,
        notification_service: NotificationService,
        reservation_repo: Any | None = None,
    ) -> None:
        """Initialize with dependencies.

        Args:
            notification_service: Service for sending notifications.
            reservation_repo: Optional reservation repository for looking up waiters.
        """
        self._notification_service = notification_service
        self._reservation_repo = reservation_repo

    def update(self, event: Event, data: dict[str, Any]) -> None:
        """Handle a book return event.

        Sends notifications to members with waiting reservations
        for the returned book.

        Args:
            event: The event type.
            data: Event data containing isbn and book_item info.
        """
        if event == Event.BOOK_RETURNED:
            isbn = data.get("isbn", "")
            if isbn and self._reservation_repo:
                waiting = self._reservation_repo.get_waiting_by_isbn(isbn)
                for reservation in waiting:
                    self._notification_service.send_notification(
                        member_id=reservation.member_id,
                        message=f"Good news! The book you reserved (ISBN: {isbn}) "
                        f"has been returned and is now available.",
                    )

        elif event == Event.RESERVATION_FULFILLED:
            member_id = data.get("member_id", "")
            book_isbn = data.get("book_isbn", "")
            if member_id:
                self._notification_service.send_notification(
                    member_id=member_id,
                    message=f"Your reservation for book (ISBN: {book_isbn}) "
                    f"has been fulfilled. Please pick up the book.",
                )

        elif event == Event.MEMBER_BLOCKED:
            member_id = data.get("member_id", "")
            total_fines = data.get("total_fines", "")
            if member_id:
                self._notification_service.send_notification(
                    member_id=member_id,
                    message=f"Your account has been blocked due to unpaid fines "
                    f"totaling ${total_fines}. Please pay your fines to regain access.",
                )

        elif event == Event.MEMBER_UNBLOCKED:
            member_id = data.get("member_id", "")
            if member_id:
                self._notification_service.send_notification(
                    member_id=member_id,
                    message="Your account has been unblocked. You can now borrow books again.",
                )
