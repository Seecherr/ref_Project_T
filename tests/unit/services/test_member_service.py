"""Unit tests for MemberService."""

import pytest

from src.models.member import Reader, Librarian, MemberStatus
from src.utils.exceptions import MemberNotFoundError, DuplicateError


class TestMemberService:
    """Tests for MemberService."""

    def test_register_reader(self, member_service):
        reader = member_service.register_reader("John Doe", "john@example.com")
        assert reader.name == "John Doe"
        assert reader.email == "john@example.com"
        assert isinstance(reader, Reader)

    def test_register_reader_with_id(self, member_service):
        reader = member_service.register_reader("John", "john@test.com", member_id="R001")
        assert reader.member_id == "R001"

    def test_register_reader_custom_limit(self, member_service):
        reader = member_service.register_reader("John", "john@test.com", max_books_limit=3)
        assert reader.max_books_limit == 3

    def test_register_reader_invalid_email(self, member_service):
        with pytest.raises(ValueError, match="email"):
            member_service.register_reader("John", "invalid")

    def test_register_reader_empty_name(self, member_service):
        with pytest.raises(ValueError):
            member_service.register_reader("", "john@test.com")

    def test_register_reader_duplicate_email(self, member_service):
        member_service.register_reader("John", "john@test.com")
        with pytest.raises(DuplicateError):
            member_service.register_reader("Jane", "john@test.com")

    def test_register_librarian(self, member_service):
        lib = member_service.register_librarian("Jane Smith", "jane@test.com", employee_id="EMP001")
        assert isinstance(lib, Librarian)
        assert lib.employee_id == "EMP001"

    def test_register_librarian_invalid_email(self, member_service):
        with pytest.raises(ValueError):
            member_service.register_librarian("Jane", "invalid")

    def test_register_librarian_duplicate_email(self, member_service):
        member_service.register_reader("John", "john@test.com")
        with pytest.raises(DuplicateError):
            member_service.register_librarian("Jane", "john@test.com")

    def test_get_member(self, member_service):
        reader = member_service.register_reader("John", "john@test.com", member_id="R001")
        result = member_service.get_member("R001")
        assert result is reader

    def test_get_member_not_found(self, member_service):
        with pytest.raises(MemberNotFoundError):
            member_service.get_member("nonexistent")

    def test_get_member_by_email(self, member_service):
        reader = member_service.register_reader("John", "john@test.com")
        result = member_service.get_member_by_email("john@test.com")
        assert result is reader

    def test_get_member_by_email_not_found(self, member_service):
        with pytest.raises(MemberNotFoundError):
            member_service.get_member_by_email("nonexistent@test.com")

    def test_get_all_members(self, member_service):
        member_service.register_reader("John", "john@test.com")
        member_service.register_librarian("Jane", "jane@test.com")
        assert len(member_service.get_all_members()) == 2

    def test_update_member_name(self, member_service):
        member_service.register_reader("John", "john@test.com", member_id="R001")
        result = member_service.update_member("R001", name="John Updated")
        assert result.name == "John Updated"

    def test_update_member_email(self, member_service):
        member_service.register_reader("John", "john@test.com", member_id="R001")
        result = member_service.update_member("R001", email="new@test.com")
        assert result.email == "new@test.com"

    def test_update_member_duplicate_email(self, member_service):
        member_service.register_reader("John", "john@test.com", member_id="R001")
        member_service.register_reader("Jane", "jane@test.com", member_id="R002")
        with pytest.raises(DuplicateError):
            member_service.update_member("R001", email="jane@test.com")

    def test_update_member_same_email(self, member_service):
        member_service.register_reader("John", "john@test.com", member_id="R001")
        result = member_service.update_member("R001", email="john@test.com")
        assert result.email == "john@test.com"

    def test_block_member(self, member_service):
        member_service.register_reader("John", "john@test.com", member_id="R001")
        result = member_service.block_member("R001")
        assert result.status == MemberStatus.BLOCKED

    def test_unblock_member(self, member_service):
        member_service.register_reader("John", "john@test.com", member_id="R001")
        member_service.block_member("R001")
        result = member_service.unblock_member("R001")
        assert result.status == MemberStatus.ACTIVE

    def test_delete_member(self, member_service):
        member_service.register_reader("John", "john@test.com", member_id="R001")
        assert member_service.delete_member("R001") is True

    def test_delete_member_not_found(self, member_service):
        with pytest.raises(MemberNotFoundError):
            member_service.delete_member("nonexistent")

    def test_is_member_active(self, member_service):
        member_service.register_reader("John", "john@test.com", member_id="R001")
        assert member_service.is_member_active("R001") is True

    def test_is_member_active_blocked(self, member_service):
        member_service.register_reader("John", "john@test.com", member_id="R001")
        member_service.block_member("R001")
        assert member_service.is_member_active("R001") is False

    def test_update_member_invalid_email(self, member_service):
        member_service.register_reader("John", "john@test.com", member_id="R001")
        with pytest.raises(ValueError):
            member_service.update_member("R001", email="invalid")

    def test_register_librarian_with_id(self, member_service):
        lib = member_service.register_librarian("Jane", "jane@test.com", member_id="L001")
        assert lib.member_id == "L001"
