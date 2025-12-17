import pytest

from src.models import ContractChange, validate_change_payload


def test_valid_payload_passes():
    payload = {
        "sections_changed": ["2.1", "5(b)"],
        "topics_touched": ["Pricing", "Termination"],
        "summary_of_the_change": "Pricing increased by 10% and early termination fee added.",
    }
    obj = validate_change_payload(payload)
    assert isinstance(obj, ContractChange)


def test_invalid_payload_raises():
    payload = {
        "sections_changed": "2.1",  # should be list
        "topics_touched": [],
        "summary_of_the_change": 123,  # should be str
    }
    with pytest.raises(ValueError):
        validate_change_payload(payload)
