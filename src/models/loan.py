"""Loan domain model for the Library Management System."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

# Default loan period in days.
DEFAULT_LOAN_PERIOD_DAYS = 14


@dataclass
class Loan:
    """Represents a book borrowing transaction.

    Tracks the lifecycle of a book item being borrowed by a member,
    including issue date, due date, and return date.
    """

    loan_id: str
    member_id: str
    book_item_barcode: str
    issue_date: date = field(default_factory=date.today)
    due_date: date = field(default=None)
    return_date: date | None = None

    def __post_init__(self) -> None:
        """Set default due date if not provided."""
        if self.due_date is None:
            self.due_date = self.issue_date + timedelta(days=DEFAULT_LOAN_PERIOD_DAYS)

    def is_active(self) -> bool:
        """Check if this loan is currently active (not returned)."""
        return self.return_date is None

    def is_overdue(self, as_of: date | None = None) -> bool:
        """Check if this loan is overdue.

        Args:
            as_of: The date to check against. Defaults to today.

        Returns:
            True if the loan is overdue as of the given date.
        """
        check_date = as_of or date.today()
        if self.return_date is not None:
            return self.return_date > self.due_date
        return check_date > self.due_date

    def days_overdue(self, as_of: date | None = None) -> int:
        """Calculate the number of days overdue.

        Args:
            as_of: The date to calculate from. Defaults to today.

        Returns:
            Number of days overdue (0 if not overdue).
        """
        check_date = as_of or date.today()
        if self.return_date is not None:
            check_date = self.return_date
        delta = (check_date - self.due_date).days
        return max(0, delta)

    def complete_return(self, return_on: date | None = None) -> None:
        """Mark this loan as returned.

        Args:
            return_on: The date of return. Defaults to today.
        """
        self.return_date = return_on or date.today()
