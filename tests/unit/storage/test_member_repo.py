"""Unit tests for InMemoryMemberRepository."""

import pytest

from src.models.member import Reader, Librarian, MemberStatus
from src.storage.in_memory_member_repository import InMemoryMemberRepository


class TestInMemoryMemberRepository:
    """Tests for InMemoryMemberRepository."""

    def test_add_and_get_by_id(self, member_repo):
        reader = Reader(member_id="R001", name="John", email="john@test.com")
        member_repo.add(reader)
        result = member_repo.get_by_id("R001")
        assert result is reader

    def test_get_by_id_nonexistent(self, member_repo):
        assert member_repo.get_by_id("nonexistent") is None

    def test_get_by_email(self, member_repo):
        reader = Reader(member_id="R001", name="John", email="john@test.com")
        member_repo.add(reader)
        result = member_repo.get_by_email("john@test.com")
        assert result is reader

    def test_get_by_email_nonexistent(self, member_repo):
        assert member_repo.get_by_email("nonexistent@test.com") is None

    def test_get_all_empty(self, member_repo):
        assert member_repo.get_all() == []

    def test_get_all_multiple(self, member_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        member_repo.add(Reader(member_id="R002", name="Jane", email="ja@t.com"))
        assert len(member_repo.get_all()) == 2

    def test_update(self, member_repo):
        reader = Reader(member_id="R001", name="John", email="john@test.com")
        member_repo.add(reader)
        reader.name = "John Updated"
        member_repo.update(reader)
        result = member_repo.get_by_id("R001")
        assert result.name == "John Updated"

    def test_delete_existing(self, member_repo):
        member_repo.add(Reader(member_id="R001", name="John", email="j@t.com"))
        assert member_repo.delete("R001") is True
        assert member_repo.get_by_id("R001") is None

    def test_delete_nonexistent(self, member_repo):
        assert member_repo.delete("nonexistent") is False

    def test_add_reader_and_librarian(self, member_repo):
        member_repo.add(Reader(member_id="R001", name="Reader", email="r@t.com"))
        member_repo.add(Librarian(member_id="L001", name="Lib", email="l@t.com"))
        assert len(member_repo.get_all()) == 2

    def test_get_by_email_with_multiple(self, member_repo):
        member_repo.add(Reader(member_id="R001", name="A", email="a@t.com"))
        member_repo.add(Reader(member_id="R002", name="B", email="b@t.com"))
        result = member_repo.get_by_email("b@t.com")
        assert result.member_id == "R002"

    def test_update_preserves_type(self, member_repo):
        reader = Reader(member_id="R001", name="John", email="j@t.com", max_books_limit=3)
        member_repo.add(reader)
        reader.max_books_limit = 10
        member_repo.update(reader)
        result = member_repo.get_by_id("R001")
        assert isinstance(result, Reader)
        assert result.max_books_limit == 10
