"""Unit tests for ReservationService."""

from datetime import datetime, timedelta

import pytest

from src.models.member import MemberStatus, Reader
from src.models.reservation import Reservation, ReservationStatus
from src.utils.exceptions import MemberBlockedError, MemberNotFoundError, ReservationError


class TestReservationServicePlace:
    """Tests for ReservationService.place_reservation."""

    def test_place_reservation(self, reservation_service, member_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        r = reservation_service.place_reservation("R001", "978-1")
        assert r.member_id == "R001"
        assert r.book_isbn == "978-1"
        assert r.status == ReservationStatus.WAITING

    def test_place_reservation_member_not_found(self, reservation_service):
        with pytest.raises(MemberNotFoundError):
            reservation_service.place_reservation("nonexistent", "978-1")

    def test_place_reservation_member_blocked(self, reservation_service, member_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com", status=MemberStatus.BLOCKED))
        with pytest.raises(MemberBlockedError):
            reservation_service.place_reservation("R001", "978-1")

    def test_place_duplicate_reservation(self, reservation_service, member_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        reservation_service.place_reservation("R001", "978-1")
        with pytest.raises(ReservationError, match="already has"):
            reservation_service.place_reservation("R001", "978-1")

    def test_place_reservation_max_limit(self, reservation_service, member_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        for i in range(5):
            reservation_service.place_reservation("R001", f"978-{i}")
        with pytest.raises(ReservationError, match="maximum"):
            reservation_service.place_reservation("R001", "978-99")

    def test_place_reservation_different_books(self, reservation_service, member_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        r1 = reservation_service.place_reservation("R001", "978-1")
        r2 = reservation_service.place_reservation("R001", "978-2")
        assert r1.book_isbn != r2.book_isbn


class TestReservationServiceCancel:
    """Tests for ReservationService.cancel_reservation."""

    def test_cancel_reservation(self, reservation_service, member_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        r = reservation_service.place_reservation("R001", "978-1")
        cancelled = reservation_service.cancel_reservation(r.reservation_id)
        assert cancelled.status == ReservationStatus.CANCELLED

    def test_cancel_nonexistent(self, reservation_service):
        with pytest.raises(ReservationError, match="not found"):
            reservation_service.cancel_reservation("nonexistent")

    def test_cancel_already_fulfilled(self, reservation_service, reservation_repo, member_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        r = Reservation(reservation_id="R1", member_id="R001", book_isbn="978-1", status=ReservationStatus.FULFILLED)
        reservation_repo.add(r)
        with pytest.raises(ReservationError, match="Cannot cancel"):
            reservation_service.cancel_reservation("R1")


class TestReservationServiceFulfill:
    """Tests for ReservationService.fulfill_next_reservation."""

    def test_fulfill_next(self, reservation_service, member_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        member_repo.add(Reader(member_id="R002", name="Jane", email="ja@t.com"))
        r1 = reservation_service.place_reservation("R001", "978-1")
        reservation_service.place_reservation("R002", "978-1")
        fulfilled = reservation_service.fulfill_next_reservation("978-1")
        assert fulfilled.reservation_id == r1.reservation_id
        assert fulfilled.status == ReservationStatus.FULFILLED

    def test_fulfill_no_reservations(self, reservation_service):
        result = reservation_service.fulfill_next_reservation("978-1")
        assert result is None

    def test_fulfill_fifo_order(self, reservation_service, member_repo, reservation_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        member_repo.add(Reader(member_id="R002", name="Jane", email="ja@t.com"))
        now = datetime.now()
        r1 = Reservation(reservation_id="R1", member_id="R001", book_isbn="978-1", created_at=now + timedelta(hours=1))
        r2 = Reservation(reservation_id="R2", member_id="R002", book_isbn="978-1", created_at=now)
        reservation_repo.add(r1)
        reservation_repo.add(r2)
        fulfilled = reservation_service.fulfill_next_reservation("978-1")
        assert fulfilled.reservation_id == "R2"  # Earlier one first


class TestReservationServiceQueries:
    """Tests for ReservationService query methods."""

    def test_get_reservation(self, reservation_service, member_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        r = reservation_service.place_reservation("R001", "978-1")
        result = reservation_service.get_reservation(r.reservation_id)
        assert result is r

    def test_get_reservation_not_found(self, reservation_service):
        with pytest.raises(ReservationError, match="not found"):
            reservation_service.get_reservation("nonexistent")

    def test_get_member_reservations(self, reservation_service, member_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        reservation_service.place_reservation("R001", "978-1")
        reservation_service.place_reservation("R001", "978-2")
        results = reservation_service.get_member_reservations("R001")
        assert len(results) == 2

    def test_get_waiting_reservations(self, reservation_service, member_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        member_repo.add(Reader(member_id="R002", name="Jane", email="ja@t.com"))
        reservation_service.place_reservation("R001", "978-1")
        reservation_service.place_reservation("R002", "978-1")
        results = reservation_service.get_waiting_reservations("978-1")
        assert len(results) == 2

    def test_get_all_reservations(self, reservation_service, member_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        reservation_service.place_reservation("R001", "978-1")
        assert len(reservation_service.get_all_reservations()) == 1
