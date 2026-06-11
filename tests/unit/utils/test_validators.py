"""Unit tests for validators."""

import pytest
from datetime import date

from src.utils.validators import (
    validate_isbn,
    validate_email,
    validate_date_range,
    validate_non_empty_string,
    validate_positive_number,
    validate_barcode,
)
from src.utils.exceptions import InvalidISBNError


class TestValidateISBN:
    """Tests for ISBN validation."""

    def test_valid_isbn_13(self):
        assert validate_isbn("9780134685991") is True

    def test_valid_isbn_13_with_hyphens(self):
        assert validate_isbn("978-0-13-468599-1") is True

    def test_valid_isbn_10(self):
        assert validate_isbn("0134685997") is True

    def test_valid_isbn_10_with_x(self):
        assert validate_isbn("123456789X") is True

    def test_invalid_isbn(self):
        with pytest.raises(InvalidISBNError):
            validate_isbn("123")

    def test_invalid_isbn_letters(self):
        with pytest.raises(InvalidISBNError):
            validate_isbn("abcdefghij")

    def test_empty_isbn(self):
        with pytest.raises(InvalidISBNError):
            validate_isbn("")

    def test_isbn_with_spaces(self):
        assert validate_isbn("978 0134685991") is True


class TestValidateEmail:
    """Tests for email validation."""

    def test_valid_email(self):
        assert validate_email("user@example.com") is True

    def test_valid_email_with_dots(self):
        assert validate_email("first.last@example.com") is True

    def test_invalid_email_no_at(self):
        assert validate_email("userexample.com") is False

    def test_invalid_email_no_domain(self):
        assert validate_email("user@") is False

    def test_invalid_email_empty(self):
        assert validate_email("") is False

    def test_valid_email_subdomain(self):
        assert validate_email("user@sub.example.com") is True


class TestValidateDateRange:
    """Tests for date range validation."""

    def test_valid_range(self):
        assert validate_date_range(date(2025, 1, 1), date(2025, 12, 31)) is True

    def test_same_date(self):
        assert validate_date_range(date(2025, 6, 1), date(2025, 6, 1)) is True

    def test_invalid_range(self):
        assert validate_date_range(date(2025, 12, 31), date(2025, 1, 1)) is False


class TestValidateNonEmptyString:
    """Tests for non-empty string validation."""

    def test_valid(self):
        assert validate_non_empty_string("hello") is True

    def test_empty(self):
        with pytest.raises(ValueError):
            validate_non_empty_string("")

    def test_whitespace_only(self):
        with pytest.raises(ValueError):
            validate_non_empty_string("   ")

    def test_custom_field_name(self):
        with pytest.raises(ValueError, match="title"):
            validate_non_empty_string("", "title")


class TestValidatePositiveNumber:
    """Tests for positive number validation."""

    def test_positive(self):
        assert validate_positive_number(5.0) is True

    def test_zero(self):
        with pytest.raises(ValueError):
            validate_positive_number(0)

    def test_negative(self):
        with pytest.raises(ValueError):
            validate_positive_number(-1.0)


class TestValidateBarcode:
    """Tests for barcode validation."""

    def test_valid(self):
        assert validate_barcode("BC001") is True

    def test_empty(self):
        with pytest.raises(ValueError):
            validate_barcode("")

    def test_whitespace(self):
        with pytest.raises(ValueError):
            validate_barcode("   ")
