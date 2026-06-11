"""Reservation domain model for the Library Management System."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime


class ReservationStatus(enum.Enum):
    """Status of a book reservation."""

    WAITING = "waiting"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


@dataclass
class Reservation:
    """Represents a reservation request for a book.

    When a book is unavailable, readers can place reservations.
    Reservations are fulfilled in order of creation (priority queue).
    """

    reservation_id: str
    member_id: str
    book_isbn: str
    created_at: datetime = field(default_factory=datetime.now)
    status: ReservationStatus = ReservationStatus.WAITING

    def is_waiting(self) -> bool:
        """Check if this reservation is still waiting."""
        return self.status == ReservationStatus.WAITING

    def fulfill(self) -> None:
        """Mark this reservation as fulfilled."""
        self.status = ReservationStatus.FULFILLED

    def cancel(self) -> None:
        """Cancel this reservation."""
        self.status = ReservationStatus.CANCELLED
