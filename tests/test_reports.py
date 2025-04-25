import pytest
from pandas import Timestamp


from src.reports import spending_by_category


def test_spend_by_category_value_error():
    result = spending_by_category(None, None)
    assert result is None


def test_spend_by_category_ok(transactions):
    result = spending_by_category(transactions, "Супермаркеты")
    assert result == [{'Дата операции': '2025-04-04 14:05:08',
  'Категория': 'Супермаркеты',
  'Сумма платежа': -1065.9}]


def test_spend_by_category_exc(transactions):
    with pytest.raises(TypeError):
        spending_by_category(transactions)
