"""Unit tests for InMemoryNotificationRepository."""

from datetime import datetime, timedelta

from src.models.notification import Notification


class TestInMemoryNotificationRepository:
    """Tests for InMemoryNotificationRepository."""

    def test_add_and_get(self, notification_repo):
        n = Notification(notification_id="N1", member_id="M1", message="Hello")
        notification_repo.add(n)
        assert notification_repo.get_by_id("N1") is n

    def test_get_nonexistent(self, notification_repo):
        assert notification_repo.get_by_id("nonexistent") is None

    def test_get_by_member(self, notification_repo):
        notification_repo.add(Notification(notification_id="N1", member_id="M1", message="A"))
        notification_repo.add(Notification(notification_id="N2", member_id="M1", message="B"))
        notification_repo.add(Notification(notification_id="N3", member_id="M2", message="C"))
        results = notification_repo.get_by_member("M1")
        assert len(results) == 2

    def test_get_by_member_empty(self, notification_repo):
        assert notification_repo.get_by_member("M1") == []

    def test_get_unread_by_member(self, notification_repo):
        n1 = Notification(notification_id="N1", member_id="M1", message="A")
        n2 = Notification(notification_id="N2", member_id="M1", message="B", is_read=True)
        notification_repo.add(n1)
        notification_repo.add(n2)
        unread = notification_repo.get_unread_by_member("M1")
        assert len(unread) == 1
        assert unread[0].notification_id == "N1"

    def test_get_unread_by_member_empty(self, notification_repo):
        assert notification_repo.get_unread_by_member("M1") == []

    def test_update(self, notification_repo):
        n = Notification(notification_id="N1", member_id="M1", message="Hello")
        notification_repo.add(n)
        n.mark_read()
        notification_repo.update(n)
        result = notification_repo.get_by_id("N1")
        assert result.is_read is True

    def test_get_all(self, notification_repo):
        notification_repo.add(Notification(notification_id="N1", member_id="M1", message="A"))
        notification_repo.add(Notification(notification_id="N2", member_id="M2", message="B"))
        assert len(notification_repo.get_all()) == 2

    def test_get_all_empty(self, notification_repo):
        assert notification_repo.get_all() == []

    def test_get_by_member_newest_first(self, notification_repo):
        now = datetime.now()
        n1 = Notification(notification_id="N1", member_id="M1", message="Old", created_at=now - timedelta(hours=2))
        n2 = Notification(notification_id="N2", member_id="M1", message="New", created_at=now)
        notification_repo.add(n1)
        notification_repo.add(n2)
        results = notification_repo.get_by_member("M1")
        assert results[0].notification_id == "N2"  # Newest first
