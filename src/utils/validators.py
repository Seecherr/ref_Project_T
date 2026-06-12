"""Input validation helpers for the Library Management System."""

import re
from datetime import date

from src.utils.exceptions import InvalidISBNError

# ISBN-13 pattern: 13 digits, optionally separated by hyphens.
ISBN_13_PATTERN = re.compile(r"^(?:\d{3}-?)?\d{1,5}-?\d{1,7}-?\d{1,7}-?\d$")

# ISBN-10 pattern: 10 digits or 9 digits + X.
ISBN_10_PATTERN = re.compile(r"^\d{9}[\dXx]$")

# Simple email pattern.
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def validate_isbn(isbn: str) -> bool:
    """Validate an ISBN format (ISBN-10 or ISBN-13).

    Args:
        isbn: The ISBN string to validate.

    Returns:
        True if the ISBN format is valid.

    Raises:
        InvalidISBNError: If the ISBN format is invalid.
    """
    cleaned = isbn.replace("-", "").replace(" ", "")
    if len(cleaned) == 13 and cleaned.isdigit():
        return True
    if len(cleaned) == 10 and (cleaned.isdigit() or (cleaned[:9].isdigit() and cleaned[9] in "Xx")):
        return True
    raise InvalidISBNError(isbn)


def validate_email(email: str) -> bool:
    """Validate an email format.

    Args:
        email: The email string to validate.

    Returns:
        True if the email format is valid, False otherwise.
    """
    return bool(EMAIL_PATTERN.match(email))


def validate_date_range(start: date, end: date) -> bool:
    """Validate that a date range is valid (start <= end).

    Args:
        start: The start date.
        end: The end date.

    Returns:
        True if start <= end, False otherwise.
    """
    return start <= end


def validate_non_empty_string(value: str, field_name: str = "value") -> bool:
    """Validate that a string is not empty or whitespace-only.

    Args:
        value: The string to validate.
        field_name: Name of the field for error messages.

    Returns:
        True if the string is not empty.

    Raises:
        ValueError: If the string is empty or whitespace-only.
    """
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return True


def validate_positive_number(value: float, field_name: str = "value") -> bool:
    """Validate that a number is positive.

    Args:
        value: The number to validate.
        field_name: Name of the field for error messages.

    Returns:
        True if the number is positive.

    Raises:
        ValueError: If the number is not positive.
    """
    if value <= 0:
        raise ValueError(f"{field_name} must be positive, got {value}")
    return True


def validate_barcode(barcode: str) -> bool:
    """Validate a barcode format (non-empty alphanumeric string).

    Args:
        barcode: The barcode string to validate.

    Returns:
        True if the barcode format is valid.

    Raises:
        ValueError: If the barcode is empty.
    """
    if not barcode or not barcode.strip():
        raise ValueError("Barcode cannot be empty")
    return True
