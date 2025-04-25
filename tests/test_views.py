import json
from unittest.mock import mock_open, patch

import pytest
import requests
from freezegun import freeze_time

from src.views import welcome_time, get_cashback, get_expenses, get_incomes, get_currency_stock, get_currency_rates


@freeze_time("2025-01-01 18:00:00")
def test_welcome_time_evening():
    result = welcome_time()
    assert result == "Добрый вечер"


@freeze_time("2025-01-01 12:00:00")
def test_welcome_time_noon():
    result = welcome_time()
    assert result == "Добрый день"


@freeze_time("2025-01-01 8:00:00")
def test_welcome_time_morning():
    result = welcome_time()
    assert result == "Доброе утро"


@freeze_time("2025-01-01 1:00:00")
def test_welcome_time_night():
    result = welcome_time()
    assert result == "Доброй ночи"


def test_get_cashback(transactions):
    result = get_cashback(transactions)
    assert result == [{'cashback': 10.65, 'last_digits': '7197', 'total_spent': 1065.9}]


def test_get_cashback_exc():
    with pytest.raises(Exception):
        get_cashback()


def test_get_expenses_ok(transactions):
    result = get_expenses(transactions)
    assert result == {'main': [{'amount': 3000.0, 'category': 'Переводы'},
          {'amount': 1138.96, 'category': 'Супермаркеты'},
          {'amount': 337.0, 'category': 'Красота'},
          {'amount': 0.0, 'category': 'Остальное'}],
 'total_amount': 4475.96,
 'transfers_and_cash': [{'amount': 3000.0, 'category': 'Переводы'}]}


def test_get_expenses_exc(transactions):
    with pytest.raises(Exception):
        get_expenses()


def test_get_incomes_ok(transactions):
    result = get_incomes(transactions, "2018-01-01 00:00:00", "2")
    assert result == {'main': [], 'total_amount': 0}


def test_get_incomes_exc(transactions):
    with pytest.raises(Exception):
        get_incomes()

def test_get_currency_stock_ok():
    mock_settings = {
        "user_stocks": ["AAPL", "MSFT"]
    }
    mock_response = {
        "data": [
            {"symbol": "AAPL", "open": 150.25},
            {"symbol": "MSFT", "open": 250.50}
        ]
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_settings))), \
            patch("requests.get") as mock_get:
        # Настраиваем мок ответа от API
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.status_code = 200
        result = get_currency_stock()
        assert len(result) == 2
        assert result[0]["stock"] == "AAPL"
        assert result[0]["price"] == 150.25
        assert result[1]["stock"] == "MSFT"
        assert result[1]["price"] == 250.50

def test_get_currency_stock_api_error():
    mock_settings = {
        "user_stocks": ["AAPL", "MSFT"]
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_settings))):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 401
            mock_get.return_value.json.return_value = {"error": "Invalid API key"}
            with pytest.raises(requests.exceptions.HTTPError):
                get_currency_stock()

def test_get_currency_stock_empty():
    mock_settings = {
        "user_stocks": []
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_settings))):
        with pytest.raises(Exception):
            get_currency_stock()


def test_get_currency_rates_api_error():
    mock_settings = {
        "user_currencies": ["USD", "EUR"]
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_settings))):
        with patch("requests.request") as mock_request:
            mock_request.return_value.status_code = 401
            mock_request.return_value.json.return_value = {"error": "Invalid API key"}
            with pytest.raises(requests.exceptions.HTTPError):
                get_currency_rates()

def test_get_currency_rates_empty():
    mock_settings = {
        "user_currencies": []
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_settings))):
        with pytest.raises(Exception):
            get_currency_rates()