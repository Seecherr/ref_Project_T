"""Unit tests for Reservation model."""

import pytest
from datetime import datetime

from src.models.reservation import Reservation, ReservationStatus


class TestReservationStatus:
    """Tests for ReservationStatus enum."""

    def test_waiting_value(self):
        assert ReservationStatus.WAITING.value == "waiting"

    def test_fulfilled_value(self):
        assert ReservationStatus.FULFILLED.value == "fulfilled"

    def test_cancelled_value(self):
        assert ReservationStatus.CANCELLED.value == "cancelled"


class TestReservation:
    """Tests for Reservation dataclass."""

    def test_creation_defaults(self, sample_reservation):
        assert sample_reservation.reservation_id == "RES001"
        assert sample_reservation.member_id == "R001"
        assert sample_reservation.book_isbn == "9780134685991"
        assert sample_reservation.status == ReservationStatus.WAITING
        assert isinstance(sample_reservation.created_at, datetime)

    def test_is_waiting_default(self, sample_reservation):
        assert sample_reservation.is_waiting() is True

    def test_is_waiting_after_fulfill(self, sample_reservation):
        sample_reservation.fulfill()
        assert sample_reservation.is_waiting() is False

    def test_fulfill(self, sample_reservation):
        sample_reservation.fulfill()
        assert sample_reservation.status == ReservationStatus.FULFILLED

    def test_cancel(self, sample_reservation):
        sample_reservation.cancel()
        assert sample_reservation.status == ReservationStatus.CANCELLED

    def test_is_waiting_after_cancel(self, sample_reservation):
        sample_reservation.cancel()
        assert sample_reservation.is_waiting() is False

    def test_created_at_is_set(self, sample_reservation):
        assert sample_reservation.created_at is not None

    def test_multiple_reservations_different_statuses(self):
        r1 = Reservation(reservation_id="R1", member_id="M1", book_isbn="ISBN1")
        r2 = Reservation(reservation_id="R2", member_id="M2", book_isbn="ISBN1")
        r1.fulfill()
        r2.cancel()
        assert r1.status == ReservationStatus.FULFILLED
        assert r2.status == ReservationStatus.CANCELLED
