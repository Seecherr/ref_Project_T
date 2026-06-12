"""Unit tests for fine calculation strategies (Strategy Pattern)."""

from decimal import Decimal

from src.utils.fine_strategy import (
    FineCalculationStrategy,
    NoFineStrategy,
    ProgressiveFineStrategy,
    StandardFineStrategy,
)


class TestStandardFineStrategy:
    """Tests for StandardFineStrategy."""

    def test_zero_days(self):
        strategy = StandardFineStrategy()
        assert strategy.calculate(0) == Decimal("0.00")

    def test_negative_days(self):
        strategy = StandardFineStrategy()
        assert strategy.calculate(-5) == Decimal("0.00")

    def test_one_day(self):
        strategy = StandardFineStrategy()
        assert strategy.calculate(1) == Decimal("0.50")

    def test_seven_days(self):
        strategy = StandardFineStrategy()
        assert strategy.calculate(7) == Decimal("3.50")

    def test_thirty_days(self):
        strategy = StandardFineStrategy()
        assert strategy.calculate(30) == Decimal("15.00")

    def test_custom_rate(self):
        strategy = StandardFineStrategy(daily_rate=Decimal("1.00"))
        assert strategy.calculate(10) == Decimal("10.00")

    def test_small_rate(self):
        strategy = StandardFineStrategy(daily_rate=Decimal("0.10"))
        assert strategy.calculate(5) == Decimal("0.50")

    def test_is_strategy(self):
        assert isinstance(StandardFineStrategy(), FineCalculationStrategy)


class TestProgressiveFineStrategy:
    """Tests for ProgressiveFineStrategy."""

    def test_zero_days(self):
        strategy = ProgressiveFineStrategy()
        assert strategy.calculate(0) == Decimal("0.00")

    def test_negative_days(self):
        strategy = ProgressiveFineStrategy()
        assert strategy.calculate(-3) == Decimal("0.00")

    def test_one_day_first_tier(self):
        strategy = ProgressiveFineStrategy()
        assert strategy.calculate(1) == Decimal("0.50")

    def test_seven_days_first_tier(self):
        strategy = ProgressiveFineStrategy()
        # 7 days x $0.50 = $3.50
        assert strategy.calculate(7) == Decimal("3.50")

    def test_eight_days_crosses_tier(self):
        strategy = ProgressiveFineStrategy()
        # 7 x $0.50 + 1 x $1.00 = $4.50
        assert strategy.calculate(8) == Decimal("4.50")

    def test_fourteen_days(self):
        strategy = ProgressiveFineStrategy()
        # 7 x $0.50 + 7 x $1.00 = $3.50 + $7.00 = $10.50
        assert strategy.calculate(14) == Decimal("10.50")

    def test_fifteen_days_crosses_third_tier(self):
        strategy = ProgressiveFineStrategy()
        # 7 x $0.50 + 7 x $1.00 + 1 x $2.00 = $12.50
        assert strategy.calculate(15) == Decimal("12.50")

    def test_thirty_days(self):
        strategy = ProgressiveFineStrategy()
        # 7 x $0.50 + 7 x $1.00 + 16 x $2.00 = $3.50 + $7.00 + $32.00 = $42.50
        assert strategy.calculate(30) == Decimal("42.50")

    def test_thirty_one_days_fourth_tier(self):
        strategy = ProgressiveFineStrategy()
        # 7 x $0.50 + 7 x $1.00 + 16 x $2.00 + 1 x $4.00 = $46.50
        assert strategy.calculate(31) == Decimal("46.50")

    def test_custom_base_rate(self):
        strategy = ProgressiveFineStrategy(base_rate=Decimal("1.00"))
        # 7 x $1.00 = $7.00 for 7 days
        assert strategy.calculate(7) == Decimal("7.00")

    def test_is_strategy(self):
        assert isinstance(ProgressiveFineStrategy(), FineCalculationStrategy)

    def test_progressive_more_than_standard(self):
        """Progressive should always be >= standard for the same base rate."""
        standard = StandardFineStrategy(daily_rate=Decimal("0.50"))
        progressive = ProgressiveFineStrategy(base_rate=Decimal("0.50"))
        for days in [8, 14, 21, 30]:
            assert progressive.calculate(days) >= standard.calculate(days)


class TestNoFineStrategy:
    """Tests for NoFineStrategy."""

    def test_zero_days(self):
        strategy = NoFineStrategy()
        assert strategy.calculate(0) == Decimal("0.00")

    def test_positive_days(self):
        strategy = NoFineStrategy()
        assert strategy.calculate(100) == Decimal("0.00")

    def test_negative_days(self):
        strategy = NoFineStrategy()
        assert strategy.calculate(-5) == Decimal("0.00")

    def test_is_strategy(self):
        assert isinstance(NoFineStrategy(), FineCalculationStrategy)
