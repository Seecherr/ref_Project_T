"""Reservation management service for the Library Management System.

Handles reservation placement, cancellation, and fulfillment with
priority queue semantics (FIFO by creation date).
"""

from __future__ import annotations

from src.models.reservation import Reservation
from src.storage.interfaces import (
    BookItemRepository,
    MemberRepository,
    ReservationRepository,
)
from src.utils.event_manager import Event, EventManager
from src.utils.exceptions import (
    MemberBlockedError,
    MemberNotFoundError,
    ReservationError,
)
from src.utils.id_generator import generate_id


class ReservationService:
    """Service for managing book reservations.

    Implements priority queue semantics — reservations are fulfilled
    in order of creation date (FIFO).
    """

    def __init__(
        self,
        reservation_repo: ReservationRepository,
        book_item_repo: BookItemRepository,
        member_repo: MemberRepository,
        event_manager: EventManager | None = None,
        max_reservations_per_member: int = 5,
    ) -> None:
        """Initialize with dependencies.

        Args:
            reservation_repo: Repository for Reservation entities.
            book_item_repo: Repository for BookItem entities.
            member_repo: Repository for Member entities.
            event_manager: Optional event manager for publishing events.
            max_reservations_per_member: Max active reservations per member.
        """
        self._reservation_repo = reservation_repo
        self._book_item_repo = book_item_repo
        self._member_repo = member_repo
        self._event_manager = event_manager or EventManager()
        self._max_reservations = max_reservations_per_member

    def place_reservation(
        self,
        member_id: str,
        book_isbn: str,
    ) -> Reservation:
        """Place a reservation for a book.

        Args:
            member_id: The member placing the reservation.
            book_isbn: The ISBN of the book to reserve.

        Returns:
            The created Reservation.

        Raises:
            MemberNotFoundError: If member not found.
            MemberBlockedError: If member is blocked.
            ReservationError: If member has too many active reservations or
                             already has a waiting reservation for this book.
        """
        # Validate member
        member = self._member_repo.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError(member_id)
        if not member.is_active():
            raise MemberBlockedError(member_id)

        # Check for existing waiting reservation for same book
        member_reservations = self._reservation_repo.get_by_member(member_id)
        waiting_for_book = [r for r in member_reservations if r.book_isbn == book_isbn and r.is_waiting()]
        if waiting_for_book:
            raise ReservationError(f"Member {member_id} already has a waiting reservation for book {book_isbn}")

        # Check max reservations limit
        active_count = sum(1 for r in member_reservations if r.is_waiting())
        if active_count >= self._max_reservations:
            raise ReservationError(
                f"Member {member_id} has reached the maximum of {self._max_reservations} active reservations"
            )

        reservation = Reservation(
            reservation_id=generate_id(),
            member_id=member_id,
            book_isbn=book_isbn,
        )
        self._reservation_repo.add(reservation)
        return reservation

    def cancel_reservation(self, reservation_id: str) -> Reservation:
        """Cancel a reservation.

        Args:
            reservation_id: The reservation to cancel.

        Returns:
            The cancelled Reservation.

        Raises:
            ReservationError: If reservation not found or not in waiting status.
        """
        reservation = self._reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ReservationError(f"Reservation not found: {reservation_id}")
        if not reservation.is_waiting():
            raise ReservationError(f"Cannot cancel reservation {reservation_id}: status is {reservation.status.value}")

        reservation.cancel()
        self._reservation_repo.update(reservation)
        return reservation

    def fulfill_next_reservation(self, book_isbn: str) -> Reservation | None:
        """Fulfill the next waiting reservation for a book (FIFO).

        This is typically called when a book is returned and becomes available.

        Args:
            book_isbn: The ISBN of the returned book.

        Returns:
            The fulfilled Reservation, or None if no waiting reservations.
        """
        waiting = self._reservation_repo.get_waiting_by_isbn(book_isbn)
        if not waiting:
            return None

        reservation = waiting[0]  # First in queue (earliest created_at)
        reservation.fulfill()
        self._reservation_repo.update(reservation)

        # Publish event
        self._event_manager.notify(
            Event.RESERVATION_FULFILLED,
            {
                "reservation": reservation,
                "member_id": reservation.member_id,
                "book_isbn": book_isbn,
            },
        )

        return reservation

    def get_reservation(self, reservation_id: str) -> Reservation:
        """Get a reservation by ID.

        Args:
            reservation_id: The reservation ID.

        Returns:
            The Reservation.

        Raises:
            ReservationError: If reservation not found.
        """
        reservation = self._reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise ReservationError(f"Reservation not found: {reservation_id}")
        return reservation

    def get_member_reservations(self, member_id: str) -> list[Reservation]:
        """Get all reservations for a member.

        Args:
            member_id: The member whose reservations to retrieve.

        Returns:
            List of reservations.
        """
        return self._reservation_repo.get_by_member(member_id)

    def get_waiting_reservations(self, book_isbn: str) -> list[Reservation]:
        """Get all waiting reservations for a book (ordered by priority).

        Args:
            book_isbn: The ISBN of the book.

        Returns:
            List of waiting reservations, ordered by creation date.
        """
        return self._reservation_repo.get_waiting_by_isbn(book_isbn)

    def get_all_reservations(self) -> list[Reservation]:
        """Get all reservations.

        Returns:
            List of all reservations.
        """
        return self._reservation_repo.get_all()
