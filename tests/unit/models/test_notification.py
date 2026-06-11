"""Unit tests for Notification model."""

import pytest
from datetime import datetime

from src.models.notification import Notification


class TestNotification:
    """Tests for Notification dataclass."""

    def test_creation_defaults(self, sample_notification):
        assert sample_notification.notification_id == "NOT001"
        assert sample_notification.member_id == "R001"
        assert sample_notification.message == "Test notification"
        assert sample_notification.is_read is False
        assert isinstance(sample_notification.created_at, datetime)

    def test_mark_read(self, sample_notification):
        sample_notification.mark_read()
        assert sample_notification.is_read is True

    def test_mark_unread(self, sample_notification):
        sample_notification.mark_read()
        sample_notification.mark_unread()
        assert sample_notification.is_read is False

    def test_mark_read_idempotent(self, sample_notification):
        sample_notification.mark_read()
        sample_notification.mark_read()
        assert sample_notification.is_read is True

    def test_mark_unread_when_already_unread(self, sample_notification):
        sample_notification.mark_unread()
        assert sample_notification.is_read is False

    def test_created_at_is_set(self, sample_notification):
        assert sample_notification.created_at is not None
