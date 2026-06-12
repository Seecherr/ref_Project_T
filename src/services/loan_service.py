"""Loan management service for the Library Management System.

Handles book borrowing and returning, enforcing business rules
such as member status checks, loan limits, and overdue detection.
"""

from __future__ import annotations

from datetime import date, timedelta

from src.models.loan import DEFAULT_LOAN_PERIOD_DAYS, Loan
from src.models.member import Reader
from src.storage.interfaces import (
    BookItemRepository,
    LoanRepository,
    MemberRepository,
)
from src.utils.event_manager import Event, EventManager
from src.utils.exceptions import (
    BookNotAvailableError,
    BookNotFoundError,
    LoanLimitExceededError,
    LoanNotFoundError,
    MemberBlockedError,
    MemberNotFoundError,
)
from src.utils.id_generator import generate_id


class LoanService:
    """Service for managing book loans.

    Orchestrates the borrowing and returning process, enforcing
    business rules and publishing events via the Observer pattern.
    """

    def __init__(
        self,
        loan_repo: LoanRepository,
        book_item_repo: BookItemRepository,
        member_repo: MemberRepository,
        event_manager: EventManager | None = None,
    ) -> None:
        """Initialize with repository and event manager dependencies.

        Args:
            loan_repo: Repository for Loan entities.
            book_item_repo: Repository for BookItem entities.
            member_repo: Repository for Member entities.
            event_manager: Optional event manager for publishing events.
        """
        self._loan_repo = loan_repo
        self._book_item_repo = book_item_repo
        self._member_repo = member_repo
        self._event_manager = event_manager or EventManager()

    def borrow_book(
        self,
        member_id: str,
        barcode: str,
        loan_period_days: int = DEFAULT_LOAN_PERIOD_DAYS,
    ) -> Loan:
        """Borrow a book item.

        Validates:
        - Member exists and is active (not blocked)
        - Member is a Reader and under their loan limit
        - Book item exists and is available

        Args:
            member_id: The borrowing member's ID.
            barcode: The barcode of the book item to borrow.
            loan_period_days: Number of days for the loan period.

        Returns:
            The created Loan.

        Raises:
            MemberNotFoundError: If member not found.
            MemberBlockedError: If member is blocked.
            LoanLimitExceededError: If member is at their loan limit.
            BookNotFoundError: If book item not found.
            BookNotAvailableError: If book item is not available.
        """
        # Validate member
        member = self._member_repo.get_by_id(member_id)
        if not member:
            raise MemberNotFoundError(member_id)
        if not member.is_active():
            raise MemberBlockedError(member_id)

        # Check loan limit for readers
        if isinstance(member, Reader) and not member.can_borrow():
            raise LoanLimitExceededError(member_id, member.max_books_limit)

        # Validate book item
        book_item = self._book_item_repo.get_by_barcode(barcode)
        if not book_item:
            raise BookNotFoundError(barcode)
        if not book_item.is_available():
            raise BookNotAvailableError(barcode)

        # Create the loan
        loan_id = generate_id()
        issue_date = date.today()
        due_date = issue_date + timedelta(days=loan_period_days)

        loan = Loan(
            loan_id=loan_id,
            member_id=member_id,
            book_item_barcode=barcode,
            issue_date=issue_date,
            due_date=due_date,
        )

        # Update book item status
        book_item.mark_loaned(due_date)
        self._book_item_repo.update(book_item)

        # Update member's borrowed count
        if isinstance(member, Reader):
            member.increment_borrowed()
            self._member_repo.update(member)

        # Save loan
        self._loan_repo.add(loan)

        return loan

    def return_book(
        self,
        barcode: str,
        return_date: date | None = None,
    ) -> Loan:
        """Return a borrowed book item.

        Args:
            barcode: The barcode of the book item being returned.
            return_date: The date of return. Defaults to today.

        Returns:
            The completed Loan.

        Raises:
            BookNotFoundError: If book item not found.
            LoanNotFoundError: If no active loan for this book item.
        """
        # Find the book item
        book_item = self._book_item_repo.get_by_barcode(barcode)
        if not book_item:
            raise BookNotFoundError(barcode)

        # Find active loan
        loan = self._loan_repo.get_active_by_book_item(barcode)
        if not loan:
            raise LoanNotFoundError(f"active loan for barcode {barcode}")

        # Complete the return
        actual_return_date = return_date or date.today()
        loan.complete_return(actual_return_date)
        self._loan_repo.update(loan)

        # Update book item status
        book_item.mark_available()
        self._book_item_repo.update(book_item)

        # Update member's borrowed count
        member = self._member_repo.get_by_id(loan.member_id)
        if member and isinstance(member, Reader):
            member.decrement_borrowed()
            self._member_repo.update(member)

        # Publish event for Observer pattern
        self._event_manager.notify(
            Event.BOOK_RETURNED,
            {
                "loan": loan,
                "book_item": book_item,
                "member_id": loan.member_id,
                "isbn": book_item.book_isbn,
            },
        )

        return loan

    def get_loan(self, loan_id: str) -> Loan:
        """Get a loan by ID.

        Args:
            loan_id: The loan ID to look up.

        Returns:
            The Loan.

        Raises:
            LoanNotFoundError: If no loan with this ID exists.
        """
        loan = self._loan_repo.get_by_id(loan_id)
        if not loan:
            raise LoanNotFoundError(loan_id)
        return loan

    def get_active_loans_by_member(self, member_id: str) -> list[Loan]:
        """Get all active loans for a member.

        Args:
            member_id: The member whose loans to retrieve.

        Returns:
            List of active loans.
        """
        return self._loan_repo.get_active_by_member(member_id)

    def get_all_loans(self) -> list[Loan]:
        """Get all loans.

        Returns:
            List of all loans.
        """
        return self._loan_repo.get_all()

    def get_overdue_loans(self, as_of: date | None = None) -> list[Loan]:
        """Get all currently overdue loans.

        Args:
            as_of: Date to check against. Defaults to today.

        Returns:
            List of overdue active loans.
        """
        check_date = as_of or date.today()
        return [loan for loan in self._loan_repo.get_all() if loan.is_active() and loan.is_overdue(check_date)]

    def get_loan_history_by_member(self, member_id: str) -> list[Loan]:
        """Get all loans (active and completed) for a member.

        Args:
            member_id: The member whose loan history to retrieve.

        Returns:
            List of all loans for the member.
        """
        return [loan for loan in self._loan_repo.get_all() if loan.member_id == member_id]
