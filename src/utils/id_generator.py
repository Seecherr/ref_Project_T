"""UUID-based ID generation utility."""

import uuid


def generate_id() -> str:
    """Generate a unique identifier using UUID4.

    Returns:
        A string representation of a new UUID4.
    """
    return str(uuid.uuid4())
