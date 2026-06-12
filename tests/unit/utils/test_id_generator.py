"""Unit tests for ID generator."""

from src.utils.id_generator import generate_id


class TestGenerateId:
    """Tests for generate_id function."""

    def test_returns_string(self):
        result = generate_id()
        assert isinstance(result, str)

    def test_unique(self):
        ids = {generate_id() for _ in range(100)}
        assert len(ids) == 100

    def test_non_empty(self):
        assert len(generate_id()) > 0

    def test_uuid_format(self):
        result = generate_id()
        assert len(result) == 36  # UUID4 format: 8-4-4-4-12
        assert result.count("-") == 4
