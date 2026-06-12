"""Custom exception hierarchy for the Library Management System.

All library-specific exceptions inherit from LibraryError to enable
broad catch-all handling when needed, while preserving specific
exception types for fine-grained error handling.
"""


class LibraryError(Exception):
    """Base exception for all library management errors."""


class BookNotFoundError(LibraryError):
    """Raised when a book or book item cannot be found."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Book not found: {identifier}")
        self.identifier = identifier


class BookNotAvailableError(LibraryError):
    """Raised when a book item is not available for borrowing."""

    def __init__(self, barcode: str) -> None:
        super().__init__(f"Book item not available: {barcode}")
        self.barcode = barcode


class MemberNotFoundError(LibraryError):
    """Raised when a member cannot be found."""

    def __init__(self, member_id: str) -> None:
        super().__init__(f"Member not found: {member_id}")
        self.member_id = member_id


class MemberBlockedError(LibraryError):
    """Raised when a blocked member attempts a restricted action."""

    def __init__(self, member_id: str) -> None:
        super().__init__(f"Member is blocked: {member_id}")
        self.member_id = member_id


class LoanLimitExceededError(LibraryError):
    """Raised when a member tries to borrow more than their limit."""

    def __init__(self, member_id: str, limit: int) -> None:
        super().__init__(f"Loan limit ({limit}) exceeded for member: {member_id}")
        self.member_id = member_id
        self.limit = limit


class LoanNotFoundError(LibraryError):
    """Raised when a loan cannot be found."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Loan not found: {identifier}")
        self.identifier = identifier


class InvalidISBNError(LibraryError):
    """Raised when an invalid ISBN format is provided."""

    def __init__(self, isbn: str) -> None:
        super().__init__(f"Invalid ISBN format: {isbn}")
        self.isbn = isbn


class DuplicateError(LibraryError):
    """Raised when attempting to add a duplicate entity."""

    def __init__(self, entity_type: str, identifier: str) -> None:
        super().__init__(f"Duplicate {entity_type}: {identifier}")
        self.entity_type = entity_type
        self.identifier = identifier


class ReservationError(LibraryError):
    """Raised for reservation-related errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class FineNotFoundError(LibraryError):
    """Raised when a fine cannot be found."""

    def __init__(self, fine_id: str) -> None:
        super().__init__(f"Fine not found: {fine_id}")
        self.fine_id = fine_id
