import pytest

from src.services import change_best_cashback

def test_change_best_cashback_ok(transactions):
    result = change_best_cashback(transactions, "2025", "4")
    assert result == {'Супермаркеты': 50.0}


def test_change_best_cashback_exc(transactions):
    with pytest.raises(TypeError):
        change_best_cashback(transactions)
