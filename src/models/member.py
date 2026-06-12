"""Member domain models for the Library Management System."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime


class MemberStatus(enum.Enum):
    """Status of a library member."""

    ACTIVE = "active"
    BLOCKED = "blocked"


@dataclass
class Member:
    """Base class for library members.

    Represents any person registered with the library.
    """

    member_id: str
    name: str
    email: str
    status: MemberStatus = MemberStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)

    def is_active(self) -> bool:
        """Check if the member account is active."""
        return self.status == MemberStatus.ACTIVE

    def block(self) -> None:
        """Block this member's account."""
        self.status = MemberStatus.BLOCKED

    def unblock(self) -> None:
        """Unblock this member's account."""
        self.status = MemberStatus.ACTIVE


@dataclass
class Reader(Member):
    """A library reader who can borrow and reserve books.

    Readers have a limit on how many books they can borrow at once.
    """

    max_books_limit: int = 5
    total_books_checked_out: int = 0

    def can_borrow(self) -> bool:
        """Check if the reader can borrow more books."""
        return self.is_active() and self.total_books_checked_out < self.max_books_limit

    def increment_borrowed(self) -> None:
        """Increment the count of currently borrowed books."""
        self.total_books_checked_out += 1

    def decrement_borrowed(self) -> None:
        """Decrement the count of currently borrowed books."""
        if self.total_books_checked_out > 0:
            self.total_books_checked_out -= 1


@dataclass
class Librarian(Member):
    """A library staff member who manages the catalog and operations.

    Librarians can issue/return books, manage members, and handle fines.
    """

    employee_id: str = ""
