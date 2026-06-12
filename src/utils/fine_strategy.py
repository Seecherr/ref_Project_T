"""Strategy Pattern: Fine calculation strategies.

Implements the Strategy GoF pattern to allow different fine calculation
algorithms to be used interchangeably. This follows the Open/Closed
principle — new strategies can be added without modifying existing code.

Strategies:
    - StandardFineStrategy: Fixed daily rate.
    - ProgressiveFineStrategy: Rate increases with overdue duration.
    - NoFineStrategy: Always returns zero (for reference-only items).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal


class FineCalculationStrategy(ABC):
    """Abstract strategy for calculating overdue fines.

    Concrete strategies implement different fine algorithms
    based on library policies.
    """

    @abstractmethod
    def calculate(self, days_overdue: int) -> Decimal:
        """Calculate the fine amount based on the number of overdue days.

        Args:
            days_overdue: Number of days past the due date.

        Returns:
            The fine amount as a Decimal.
        """
        ...  # pragma: no cover


class StandardFineStrategy(FineCalculationStrategy):
    """Fixed daily rate fine strategy.

    Charges a constant rate per day overdue.
    Example: $0.50 per day x 10 days = $5.00
    """

    def __init__(self, daily_rate: Decimal = Decimal("0.50")) -> None:
        """Initialize with a daily fine rate.

        Args:
            daily_rate: The fixed rate charged per overdue day.
        """
        self.daily_rate = daily_rate

    def calculate(self, days_overdue: int) -> Decimal:
        """Calculate fine as days x daily_rate.

        Args:
            days_overdue: Number of days past the due date.

        Returns:
            The fine amount. Returns 0 if days_overdue <= 0.
        """
        if days_overdue <= 0:
            return Decimal("0.00")
        return self.daily_rate * days_overdue


class ProgressiveFineStrategy(FineCalculationStrategy):
    """Progressive fine strategy with increasing rates.

    Rate increases based on how long the book is overdue:
    - Days 1-7:   base rate (e.g., $0.50/day)
    - Days 8-14:  2x base rate (e.g., $1.00/day)
    - Days 15-30: 4x base rate (e.g., $2.00/day)
    - Days 31+:   8x base rate (e.g., $4.00/day)
    """

    def __init__(self, base_rate: Decimal = Decimal("0.50")) -> None:
        """Initialize with a base fine rate.

        Args:
            base_rate: The base rate for the first tier (days 1-7).
        """
        self.base_rate = base_rate
        self.tiers: list[tuple[int, Decimal]] = [
            (7, base_rate),
            (14, base_rate * 2),
            (30, base_rate * 4),
            (999999, base_rate * 8),
        ]

    def calculate(self, days_overdue: int) -> Decimal:
        """Calculate fine using progressive tiers.

        Args:
            days_overdue: Number of days past the due date.

        Returns:
            The total fine amount summed across tiers.
        """
        if days_overdue <= 0:
            return Decimal("0.00")

        total = Decimal("0.00")
        remaining_days = days_overdue
        prev_limit = 0

        for limit, rate in self.tiers:
            if remaining_days <= 0:
                break
            tier_days = min(remaining_days, limit - prev_limit)
            total += rate * tier_days
            remaining_days -= tier_days
            prev_limit = limit

        return total


class NoFineStrategy(FineCalculationStrategy):
    """No-fine strategy for reference-only or special items.

    Always returns zero regardless of overdue duration.
    Useful for items that should never incur fines.
    """

    def calculate(self, days_overdue: int) -> Decimal:
        """Always returns zero.

        Args:
            days_overdue: Number of days past the due date (ignored).

        Returns:
            Decimal zero.
        """
        return Decimal("0.00")
