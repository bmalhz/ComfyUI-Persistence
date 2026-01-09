import pytest
from pathlib import Path

from image_bank import get_bank_fingerprint, is_bank_valid


@pytest.mark.unit
class TestImageBank:
    """Tests for Bank utility functions."""

    def test_bank_fingerprint_from_str(self):
        bank_id = "some-id"
        assert bank_id == get_bank_fingerprint(bank_id)

    def test_bank_fingerprint_from_dict(self):
        bank_id1 = {
            "key1": "value1"
        }
        bank_fingerprint1 = get_bank_fingerprint(bank_id1)
        # fingerprint should be a hex encoded sha256
        assert bank_id1 != bank_fingerprint1

    def test_is_bank_valid_1(self):
        bank_path = Path(__file__).parent / "data" / "bank1"
        assert is_bank_valid(bank_path=str(bank_path)) is True

    def test_is_bank_valid_2(self):
        bank_path = Path(__file__).parent / "data" / "missing_bank"
        assert is_bank_valid(bank_path=str(bank_path)) is False
