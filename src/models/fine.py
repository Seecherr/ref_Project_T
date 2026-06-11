"""Fine domain model for the Library Management System."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass
class Fine:
    """Represents a monetary fine for an overdue book return.

    Fines are linked to a specific loan and member, and can be
    paid in full or partially.
    """

    fine_id: str
    loan_id: str
    member_id: str
    amount: Decimal
    paid: Decimal = Decimal("0.00")
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def outstanding(self) -> Decimal:
        """Calculate the remaining unpaid amount."""
        return self.amount - self.paid

    def is_fully_paid(self) -> bool:
        """Check if this fine has been fully paid."""
        return self.paid >= self.amount

    def pay(self, payment: Decimal) -> Decimal:
        """Apply a payment towards this fine.

        Args:
            payment: The amount to pay.

        Returns:
            The remaining outstanding amount after payment.

        Raises:
            ValueError: If payment amount is negative.
        """
        if payment < Decimal("0"):
            raise ValueError("Payment amount cannot be negative")
        self.paid = min(self.paid + payment, self.amount)
        return self.outstanding
