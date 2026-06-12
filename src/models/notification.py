"""Notification domain model for the Library Management System."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Notification:
    """Represents a notification sent to a library member.

    Used by the Observer pattern to notify readers about
    book availability, fines, and other events.
    """

    notification_id: str
    member_id: str
    message: str
    created_at: datetime = field(default_factory=datetime.now)
    is_read: bool = False

    def mark_read(self) -> None:
        """Mark this notification as read."""
        self.is_read = True

    def mark_unread(self) -> None:
        """Mark this notification as unread."""
        self.is_read = False
