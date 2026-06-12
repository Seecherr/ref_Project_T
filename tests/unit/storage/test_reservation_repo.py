"""Unit tests for InMemoryReservationRepository."""

from datetime import datetime, timedelta

from src.models.reservation import Reservation, ReservationStatus


class TestInMemoryReservationRepository:
    """Tests for InMemoryReservationRepository."""

    def test_add_and_get(self, reservation_repo):
        r = Reservation(reservation_id="R1", member_id="M1", book_isbn="978-1")
        reservation_repo.add(r)
        assert reservation_repo.get_by_id("R1") is r

    def test_get_nonexistent(self, reservation_repo):
        assert reservation_repo.get_by_id("nonexistent") is None

    def test_get_waiting_by_isbn(self, reservation_repo):
        reservation_repo.add(Reservation(reservation_id="R1", member_id="M1", book_isbn="978-1"))
        reservation_repo.add(Reservation(reservation_id="R2", member_id="M2", book_isbn="978-1"))
        fulfilled = Reservation(reservation_id="R3", member_id="M3", book_isbn="978-1")
        fulfilled.fulfill()
        reservation_repo.add(fulfilled)
        waiting = reservation_repo.get_waiting_by_isbn("978-1")
        assert len(waiting) == 2

    def test_get_waiting_by_isbn_fifo_order(self, reservation_repo):
        now = datetime.now()
        r1 = Reservation(reservation_id="R1", member_id="M1", book_isbn="978-1", created_at=now + timedelta(hours=1))
        r2 = Reservation(reservation_id="R2", member_id="M2", book_isbn="978-1", created_at=now)
        reservation_repo.add(r1)
        reservation_repo.add(r2)
        waiting = reservation_repo.get_waiting_by_isbn("978-1")
        assert waiting[0].reservation_id == "R2"  # Earlier timestamp first
        assert waiting[1].reservation_id == "R1"

    def test_get_waiting_by_isbn_empty(self, reservation_repo):
        assert reservation_repo.get_waiting_by_isbn("978-1") == []

    def test_get_by_member(self, reservation_repo):
        reservation_repo.add(Reservation(reservation_id="R1", member_id="M1", book_isbn="978-1"))
        reservation_repo.add(Reservation(reservation_id="R2", member_id="M1", book_isbn="978-2"))
        reservation_repo.add(Reservation(reservation_id="R3", member_id="M2", book_isbn="978-1"))
        results = reservation_repo.get_by_member("M1")
        assert len(results) == 2

    def test_get_by_member_empty(self, reservation_repo):
        assert reservation_repo.get_by_member("M1") == []

    def test_get_all(self, reservation_repo):
        reservation_repo.add(Reservation(reservation_id="R1", member_id="M1", book_isbn="978-1"))
        reservation_repo.add(Reservation(reservation_id="R2", member_id="M2", book_isbn="978-2"))
        assert len(reservation_repo.get_all()) == 2

    def test_get_all_empty(self, reservation_repo):
        assert reservation_repo.get_all() == []

    def test_update(self, reservation_repo):
        r = Reservation(reservation_id="R1", member_id="M1", book_isbn="978-1")
        reservation_repo.add(r)
        r.fulfill()
        reservation_repo.update(r)
        result = reservation_repo.get_by_id("R1")
        assert result.status == ReservationStatus.FULFILLED

    def test_cancelled_not_in_waiting(self, reservation_repo):
        r = Reservation(reservation_id="R1", member_id="M1", book_isbn="978-1")
        r.cancel()
        reservation_repo.add(r)
        assert reservation_repo.get_waiting_by_isbn("978-1") == []

    def test_get_waiting_different_isbn(self, reservation_repo):
        reservation_repo.add(Reservation(reservation_id="R1", member_id="M1", book_isbn="978-1"))
        reservation_repo.add(Reservation(reservation_id="R2", member_id="M2", book_isbn="978-2"))
        assert len(reservation_repo.get_waiting_by_isbn("978-1")) == 1
