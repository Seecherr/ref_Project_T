"""Fine management service for the Library Management System.

Handles fine calculation (using Strategy pattern), payment processing,
and auto-blocking of members with excessive unpaid fines.
"""

from __future__ import annotations

from decimal import Decimal

from src.models.fine import Fine
from src.models.loan import Loan
from src.storage.interfaces import FineRepository, MemberRepository
from src.utils.event_manager import Event, EventManager
from src.utils.exceptions import FineNotFoundError
from src.utils.fine_strategy import FineCalculationStrategy, StandardFineStrategy
from src.utils.id_generator import generate_id

# Default threshold for auto-blocking a member.
DEFAULT_BLOCK_THRESHOLD = Decimal("25.00")


class FineService:
    """Service for managing fines.

    Uses the Strategy pattern for fine calculation, allowing different
    algorithms to be injected (standard, progressive, no-fine).
    """

    def __init__(
        self,
        fine_repo: FineRepository,
        member_repo: MemberRepository,
        fine_strategy: FineCalculationStrategy | None = None,
        event_manager: EventManager | None = None,
        block_threshold: Decimal = DEFAULT_BLOCK_THRESHOLD,
    ) -> None:
        """Initialize with dependencies.

        Args:
            fine_repo: Repository for Fine entities.
            member_repo: Repository for Member entities.
            fine_strategy: Strategy for calculating fines. Defaults to StandardFineStrategy.
            event_manager: Optional event manager for publishing events.
            block_threshold: Total unpaid fines threshold for auto-blocking.
        """
        self._fine_repo = fine_repo
        self._member_repo = member_repo
        self._strategy = fine_strategy or StandardFineStrategy()
        self._event_manager = event_manager or EventManager()
        self._block_threshold = block_threshold

    def set_strategy(self, strategy: FineCalculationStrategy) -> None:
        """Change the fine calculation strategy at runtime.

        Args:
            strategy: The new strategy to use.
        """
        self._strategy = strategy

    def calculate_fine(self, loan: Loan) -> Decimal:
        """Calculate the fine for a loan based on overdue days.

        Args:
            loan: The loan to calculate fine for.

        Returns:
            The calculated fine amount.
        """
        days = loan.days_overdue()
        return self._strategy.calculate(days)

    def create_fine(self, loan: Loan) -> Fine | None:
        """Create a fine for an overdue loan if applicable.

        Args:
            loan: The overdue loan.

        Returns:
            The created Fine, or None if no fine is due.
        """
        amount = self.calculate_fine(loan)
        if amount <= Decimal("0"):
            return None

        # Check if fine already exists for this loan
        existing = self._fine_repo.get_by_loan(loan.loan_id)
        if existing:
            return existing

        fine = Fine(
            fine_id=generate_id(),
            loan_id=loan.loan_id,
            member_id=loan.member_id,
            amount=amount,
        )
        self._fine_repo.add(fine)

        # Publish fine created event
        self._event_manager.notify(
            Event.FINE_CREATED,
            {"fine": fine, "loan": loan},
        )

        # Check if member should be auto-blocked
        self._check_auto_block(loan.member_id)

        return fine

    def pay_fine(self, fine_id: str, payment: Decimal) -> Fine:
        """Apply a payment to a fine.

        Args:
            fine_id: The fine to pay.
            payment: The payment amount.

        Returns:
            The updated Fine.

        Raises:
            FineNotFoundError: If no fine with this ID exists.
            ValueError: If payment amount is negative.
        """
        fine = self._fine_repo.get_by_id(fine_id)
        if not fine:
            raise FineNotFoundError(fine_id)

        fine.pay(payment)
        self._fine_repo.update(fine)

        # Check if member should be unblocked after payment
        if fine.is_fully_paid():
            self._check_auto_unblock(fine.member_id)

        return fine

    def get_fine(self, fine_id: str) -> Fine:
        """Get a fine by ID.

        Args:
            fine_id: The fine ID to look up.

        Returns:
            The Fine.

        Raises:
            FineNotFoundError: If no fine with this ID exists.
        """
        fine = self._fine_repo.get_by_id(fine_id)
        if not fine:
            raise FineNotFoundError(fine_id)
        return fine

    def get_unpaid_fines(self, member_id: str) -> list[Fine]:
        """Get all unpaid fines for a member.

        Args:
            member_id: The member whose fines to retrieve.

        Returns:
            List of unpaid fines.
        """
        return self._fine_repo.get_unpaid_by_member(member_id)

    def get_total_unpaid(self, member_id: str) -> Decimal:
        """Get the total unpaid fine amount for a member.

        Args:
            member_id: The member to check.

        Returns:
            Total outstanding fine amount.
        """
        fines = self.get_unpaid_fines(member_id)
        return sum((f.outstanding for f in fines), Decimal("0.00"))

    def get_all_fines(self) -> list[Fine]:
        """Get all fines.

        Returns:
            List of all fines.
        """
        return self._fine_repo.get_all()

    def _check_auto_block(self, member_id: str) -> None:
        """Auto-block a member if total unpaid fines exceed threshold."""
        total = self.get_total_unpaid(member_id)
        if total >= self._block_threshold:
            member = self._member_repo.get_by_id(member_id)
            if member and member.is_active():
                member.block()
                self._member_repo.update(member)
                self._event_manager.notify(
                    Event.MEMBER_BLOCKED,
                    {"member_id": member_id, "total_fines": total},
                )

    def _check_auto_unblock(self, member_id: str) -> None:
        """Auto-unblock a member if all fines are paid."""
        total = self.get_total_unpaid(member_id)
        if total < self._block_threshold:
            member = self._member_repo.get_by_id(member_id)
            if member and not member.is_active():
                member.unblock()
                self._member_repo.update(member)
                self._event_manager.notify(
                    Event.MEMBER_UNBLOCKED,
                    {"member_id": member_id},
                )
