"""In-memory implementation of Member repository."""

from __future__ import annotations

from src.models.member import Member
from src.storage.interfaces import MemberRepository


class InMemoryMemberRepository(MemberRepository):
    """Dictionary-based in-memory storage for Member entities.

    Members are keyed by member_id, with a secondary index by email.
    """

    def __init__(self) -> None:
        self._members: dict[str, Member] = {}

    def add(self, member: Member) -> None:
        """Add a member."""
        self._members[member.member_id] = member

    def get_by_id(self, member_id: str) -> Member | None:
        """Get a member by ID."""
        return self._members.get(member_id)

    def get_by_email(self, email: str) -> Member | None:
        """Get a member by email."""
        for member in self._members.values():
            if member.email == email:
                return member
        return None

    def get_all(self) -> list[Member]:
        """Get all members."""
        return list(self._members.values())

    def update(self, member: Member) -> None:
        """Update a member."""
        self._members[member.member_id] = member

    def delete(self, member_id: str) -> bool:
        """Delete a member by ID."""
        if member_id in self._members:
            del self._members[member_id]
            return True
        return False
