"""In-memory implementation of Notification repository."""

from __future__ import annotations

from typing import Optional

from src.models.notification import Notification
from src.storage.interfaces import NotificationRepository


class InMemoryNotificationRepository(NotificationRepository):
    """Dictionary-based in-memory storage for Notification entities."""

    def __init__(self) -> None:
        self._notifications: dict[str, Notification] = {}

    def add(self, notification: Notification) -> None:
        """Add a notification."""
        self._notifications[notification.notification_id] = notification

    def get_by_member(self, member_id: str) -> list[Notification]:
        """Get all notifications for a member, newest first."""
        notifications = [
            n for n in self._notifications.values()
            if n.member_id == member_id
        ]
        return sorted(notifications, key=lambda n: n.created_at, reverse=True)

    def get_unread_by_member(self, member_id: str) -> list[Notification]:
        """Get unread notifications for a member, newest first."""
        notifications = [
            n for n in self._notifications.values()
            if n.member_id == member_id and not n.is_read
        ]
        return sorted(notifications, key=lambda n: n.created_at, reverse=True)

    def get_by_id(self, notification_id: str) -> Optional[Notification]:
        """Get a notification by ID."""
        return self._notifications.get(notification_id)

    def update(self, notification: Notification) -> None:
        """Update a notification."""
        self._notifications[notification.notification_id] = notification

    def get_all(self) -> list[Notification]:
        """Get all notifications."""
        return list(self._notifications.values())
