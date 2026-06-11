"""Member management service for the Library Management System.

Handles member registration, updates, blocking/unblocking, and lookups.
"""

from __future__ import annotations

from typing import Optional

from src.models.member import Member, Reader, Librarian, MemberStatus
from src.storage.interfaces import MemberRepository
from src.utils.exceptions import (
    MemberNotFoundError,
    MemberBlockedError,
    DuplicateError,
)
from src.utils.id_generator import generate_id
from src.utils.validators import validate_email, validate_non_empty_string


class MemberService:
    """Service for managing library members.

    Provides operations for registering, updating, blocking, and
    looking up members (readers and librarians).
    """

    def __init__(self, member_repo: MemberRepository) -> None:
        """Initialize with repository dependency.

        Args:
            member_repo: Repository for Member entities.
        """
        self._member_repo = member_repo

    def register_reader(
        self,
        name: str,
        email: str,
        member_id: Optional[str] = None,
        max_books_limit: int = 5,
    ) -> Reader:
        """Register a new reader.

        Args:
            name: Reader's full name.
            email: Reader's email address.
            member_id: Optional ID. Generated if not provided.
            max_books_limit: Maximum books the reader can borrow at once.

        Returns:
            The created Reader.

        Raises:
            ValueError: If name is empty or email is invalid.
            DuplicateError: If email is already registered.
        """
        validate_non_empty_string(name, "name")
        if not validate_email(email):
            raise ValueError(f"Invalid email format: {email}")

        if self._member_repo.get_by_email(email):
            raise DuplicateError("Member", email)

        if member_id is None:
            member_id = generate_id()

        reader = Reader(
            member_id=member_id,
            name=name,
            email=email,
            max_books_limit=max_books_limit,
        )
        self._member_repo.add(reader)
        return reader

    def register_librarian(
        self,
        name: str,
        email: str,
        employee_id: str = "",
        member_id: Optional[str] = None,
    ) -> Librarian:
        """Register a new librarian.

        Args:
            name: Librarian's full name.
            email: Librarian's email address.
            employee_id: Employee ID.
            member_id: Optional ID. Generated if not provided.

        Returns:
            The created Librarian.

        Raises:
            ValueError: If name is empty or email is invalid.
            DuplicateError: If email is already registered.
        """
        validate_non_empty_string(name, "name")
        if not validate_email(email):
            raise ValueError(f"Invalid email format: {email}")

        if self._member_repo.get_by_email(email):
            raise DuplicateError("Member", email)

        if member_id is None:
            member_id = generate_id()

        librarian = Librarian(
            member_id=member_id,
            name=name,
            email=email,
            employee_id=employee_id,
        )
        self._member_repo.add(librarian)
        return librarian

    def get_member(self, member_id: str) -> Member:
        """Get a member by ID.

        Args:
            member_id: The member ID to look up.

        Returns:
            The Member.

        Raises:
            MemberNotFoundError: If no member with this ID exists.
        """
        member = self._member_repo.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError(member_id)
        return member

    def get_member_by_email(self, email: str) -> Member:
        """Get a member by email.

        Args:
            email: The email to look up.

        Returns:
            The Member.

        Raises:
            MemberNotFoundError: If no member with this email exists.
        """
        member = self._member_repo.get_by_email(email)
        if not member:
            raise MemberNotFoundError(email)
        return member

    def get_all_members(self) -> list[Member]:
        """Get all registered members.

        Returns:
            List of all members.
        """
        return self._member_repo.get_all()

    def update_member(
        self,
        member_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Member:
        """Update a member's information.

        Args:
            member_id: The member to update.
            name: New name (or None to keep current).
            email: New email (or None to keep current).

        Returns:
            The updated Member.

        Raises:
            MemberNotFoundError: If member not found.
            ValueError: If new name is empty or new email is invalid.
            DuplicateError: If new email is already in use by another member.
        """
        member = self.get_member(member_id)

        if name is not None:
            validate_non_empty_string(name, "name")
            member.name = name

        if email is not None:
            if not validate_email(email):
                raise ValueError(f"Invalid email format: {email}")
            existing = self._member_repo.get_by_email(email)
            if existing and existing.member_id != member_id:
                raise DuplicateError("Member", email)
            member.email = email

        self._member_repo.update(member)
        return member

    def block_member(self, member_id: str) -> Member:
        """Block a member's account.

        Args:
            member_id: The member to block.

        Returns:
            The blocked Member.

        Raises:
            MemberNotFoundError: If member not found.
        """
        member = self.get_member(member_id)
        member.block()
        self._member_repo.update(member)
        return member

    def unblock_member(self, member_id: str) -> Member:
        """Unblock a member's account.

        Args:
            member_id: The member to unblock.

        Returns:
            The unblocked Member.

        Raises:
            MemberNotFoundError: If member not found.
        """
        member = self.get_member(member_id)
        member.unblock()
        self._member_repo.update(member)
        return member

    def delete_member(self, member_id: str) -> bool:
        """Delete a member.

        Args:
            member_id: The member to delete.

        Returns:
            True if the member was deleted.

        Raises:
            MemberNotFoundError: If member not found.
        """
        self.get_member(member_id)  # Verify existence
        return self._member_repo.delete(member_id)

    def is_member_active(self, member_id: str) -> bool:
        """Check if a member is active.

        Args:
            member_id: The member to check.

        Returns:
            True if the member is active.

        Raises:
            MemberNotFoundError: If member not found.
        """
        member = self.get_member(member_id)
        return member.is_active()
