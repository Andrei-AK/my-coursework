from unittest.mock import patch

import pandas as pd
import pytest

from src.reports import spending_by_category

def test_spend_by_category_ValueError():
    result = spending_by_category(None,None)
    assert result is None

def test_spend_by_category_ok(transactions):
    print(f"\n{transactions}")
    result = spending_by_category(transactions, "Супермаркеты")
    print(result)
    assert result == {'Дата операции': {}, 'Категория': {}, 'Сумма платежа': {}}