"""Unit tests for Member, Reader, and Librarian models."""

from datetime import datetime

from src.models.member import Librarian, Member, MemberStatus, Reader


class TestMemberStatus:
    """Tests for MemberStatus enum."""

    def test_active_value(self):
        assert MemberStatus.ACTIVE.value == "active"

    def test_blocked_value(self):
        assert MemberStatus.BLOCKED.value == "blocked"


class TestMember:
    """Tests for Member base class."""

    def test_creation_defaults(self):
        m = Member(member_id="M001", name="Test", email="test@test.com")
        assert m.member_id == "M001"
        assert m.name == "Test"
        assert m.email == "test@test.com"
        assert m.status == MemberStatus.ACTIVE
        assert isinstance(m.created_at, datetime)

    def test_is_active_default(self):
        m = Member(member_id="M001", name="Test", email="test@test.com")
        assert m.is_active() is True

    def test_block(self):
        m = Member(member_id="M001", name="Test", email="test@test.com")
        m.block()
        assert m.status == MemberStatus.BLOCKED
        assert m.is_active() is False

    def test_unblock(self):
        m = Member(member_id="M001", name="Test", email="test@test.com")
        m.block()
        m.unblock()
        assert m.status == MemberStatus.ACTIVE
        assert m.is_active() is True


class TestReader:
    """Tests for Reader subclass."""

    def test_creation_defaults(self, sample_reader):
        assert sample_reader.max_books_limit == 5
        assert sample_reader.total_books_checked_out == 0

    def test_can_borrow_initial(self, sample_reader):
        assert sample_reader.can_borrow() is True

    def test_can_borrow_at_limit(self):
        reader = Reader(member_id="R001", name="Test", email="t@t.com", total_books_checked_out=5)
        assert reader.can_borrow() is False

    def test_can_borrow_when_blocked(self, sample_reader):
        sample_reader.block()
        assert sample_reader.can_borrow() is False

    def test_increment_borrowed(self, sample_reader):
        sample_reader.increment_borrowed()
        assert sample_reader.total_books_checked_out == 1

    def test_decrement_borrowed(self, sample_reader):
        sample_reader.increment_borrowed()
        sample_reader.increment_borrowed()
        sample_reader.decrement_borrowed()
        assert sample_reader.total_books_checked_out == 1

    def test_decrement_borrowed_at_zero(self, sample_reader):
        sample_reader.decrement_borrowed()
        assert sample_reader.total_books_checked_out == 0

    def test_custom_limit(self):
        reader = Reader(member_id="R001", name="Test", email="t@t.com", max_books_limit=3)
        assert reader.max_books_limit == 3

    def test_reader_inherits_member(self, sample_reader):
        assert isinstance(sample_reader, Member)

    def test_reader_block_unblock_cycle(self, sample_reader):
        sample_reader.block()
        assert not sample_reader.can_borrow()
        sample_reader.unblock()
        assert sample_reader.can_borrow()


class TestLibrarian:
    """Tests for Librarian subclass."""

    def test_creation_with_employee_id(self, sample_librarian):
        assert sample_librarian.employee_id == "EMP001"

    def test_creation_defaults(self):
        lib = Librarian(member_id="L001", name="Test", email="lib@test.com")
        assert lib.employee_id == ""

    def test_librarian_inherits_member(self, sample_librarian):
        assert isinstance(sample_librarian, Member)

    def test_librarian_is_active(self, sample_librarian):
        assert sample_librarian.is_active() is True
