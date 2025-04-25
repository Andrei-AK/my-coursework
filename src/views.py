import json
import os
from datetime import datetime as dt
from datetime import time as t
from urllib.error import HTTPError

import pandas as pd
from dateutil.relativedelta import relativedelta
from pandas.core.interchange.dataframe_protocol import DataFrame
from typing_extensions import Optional
import requests
from dotenv import load_dotenv

from src.decirators import write_logs

load_dotenv()
PATH_TO_JSON_SETTINGS = os.getenv("PATH_TO_JSON_SETTINGS")
APIKEY = os.getenv("APIKEY")
APIKEY1 = os.getenv("APIKEY1")

headers = {"apikey": APIKEY}


@write_logs
def welcome_time():
    """Выводим приветствие в зависимости от текущего времени"""
    now_time = dt.now().time()
    if t(23, 0, 0) <= now_time or now_time <= t(4, 0, 0):
        message = "Доброй ночи"
    elif t(4, 0, 0) < now_time <= t(11, 0, 0):
        message = "Доброе утро"
    elif t(11, 0, 0) < now_time <= t(17, 0, 0):
        message = "Добрый день"
    else:
        message = "Добрый вечер"
    return message


def get_cashback(transactions, date = None):
    """Считаем сумму кэшбэка по операциям"""
    try:
        if date is None:
            end_date = dt.now()
            end_date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            end_date = dt.strptime(date, "%Y-%m-%d %H:%M:%S")
        days = end_date.day - 1
        start_date = end_date - relativedelta(days=days)
        start_date = start_date.replace(hour=0, minute=0, second=0)
        transactions = (
            transactions[
                (pd.notna(transactions["Номер карты"]))
                & (pd.notna(transactions["Сумма платежа"]))
                & (transactions["Сумма платежа"] < 0)
                & (transactions["Дата операции"] >= start_date)
                & (transactions["Дата операции"] < end_date)
            ]
            .groupby(["Номер карты"])[["Сумма платежа", "Кэшбэк"]]
            .sum()
            .reset_index()
        )
        transactions["Сумма платежа"] = abs(transactions["Сумма платежа"])
        transactions["Кэшбэк"] = transactions["Сумма платежа"] * 100 // 100 / 100
        transactions["Номер карты"] = transactions["Номер карты"].str.findall(r"\w+").str[0]
        transactions = transactions.rename(
            columns={"Номер карты": "last_digits", "Сумма платежа": "total_spent", "Кэшбэк": "cashback"}
        )
        card_cashback = transactions[["last_digits", "total_spent", "cashback"]].to_dict(orient="records")
        return card_cashback
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        raise e


@write_logs
def get_expenses(transactions: pd.DataFrame) -> dict:
    """Обрабатываем DataFrame и формируем словарь с выборкой расходов"""
    try:
        result = {"total_amount": "", "main": "", "transfers_and_cash": ""}
        # Фильтруем DataFrame
        transfers = transactions[
            (transactions["Категория"] == "Переводы")
            & (transactions["Статус"] == "OK")
            & (transactions["Сумма платежа"] < 0)
        ]
        transfers = (
            transfers[["Категория", "Сумма платежа"]]
            .groupby("Категория")["Сумма платежа"]
            .sum()
            .reset_index()
            .rename(columns={"Категория": "category", "Сумма платежа": "amount"})
        )
        transfers["amount"] = transfers["amount"].abs()
        cash = transactions[
            (transactions["Категория"] == "Наличные")
            & (transactions["Статус"] == "OK")
            & (transactions["Сумма платежа"] < 0)
        ]
        cash = (
            cash[["Категория", "Сумма платежа"]]
            .groupby("Категория")["Сумма платежа"]
            .sum()
            .reset_index()
            .rename(columns={"Категория": "category", "Сумма платежа": "amount"})
        )
        cash["amount"] = cash["amount"].abs()

        filtered_expenses = transactions[(transactions["Сумма платежа"] < 0) & (transactions["Статус"] == "OK")]
        total_expenses = float(abs(filtered_expenses["Сумма платежа"].sum()))
        amount_and_category = (
            filtered_expenses[["Категория", "Сумма платежа"]]
            .groupby("Категория")["Сумма платежа"]
            .sum()
            .reset_index()
            .rename(columns={"Категория": "category", "Сумма платежа": "amount"})
            .sort_values(["amount"])
        )
        amount_and_category["amount"] = amount_and_category["amount"].abs()
        main_category = amount_and_category.iloc[:7]
        other_category = pd.DataFrame({"category": ["Остальное"], "amount": amount_and_category["amount"].iloc[7:].sum()})
        # Объеденяем DataFrame и преобразуем в список словарей
        result_category = pd.concat([main_category, other_category]).to_dict(orient="records")
        transfers_and_cash = (
            pd.concat([cash, transfers]).sort_values(["amount"], ascending=False).to_dict(orient="records")
        )
        # Записвыаем данные в новый словарь
        result["total_amount"] = total_expenses
        result["main"] = result_category
        result["transfers_and_cash"] = transfers_and_cash
        return result
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        raise e


@write_logs
def get_incomes(transactions, date, duration: Optional[str] = 1):
    """Получаем суммы поступлеий"""
    try:
        result = {"total_amount": "", "main": ""}
        start_date = dt.strptime(date, "%Y-%m-%d %H:%M:%S")
        end_date = start_date - relativedelta(month=int(duration))
        transactions = transactions[["Дата операции", "Категория", "Сумма платежа"]]
        transactions = transactions[
            (transactions["Сумма платежа"] > 0)
            & (transactions["Дата операции"] > end_date)
            & (transactions["Дата операции"] <= start_date)
        ]
        total_amount = int(transactions["Сумма платежа"].sum())
        incomes_by_categories = (
            transactions.groupby("Категория")["Сумма платежа"]
            .sum()
            .reset_index()
            .sort_values(["Сумма платежа"], ascending=False)
            .rename(columns={"Категория": "category", "Сумма платежа": "amount"})
        )
        result["total_amount"] = total_amount
        result["main"] = incomes_by_categories.to_dict(orient="records")
        return result
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        raise e


def get_currency_stock():
    """Получаем актуальные курсы акций"""
    with open(PATH_TO_JSON_SETTINGS) as f:
        user_settings = json.load(f)
    if user_settings["user_stocks"]:
        stocks = ",".join(currency for currency in user_settings["user_stocks"])
        response = requests.get(f"http://api.marketstack.com/v2/eod/latest?access_key={APIKEY1}&symbols={stocks}")
        if response.status_code == 200:
            response = response.json()
            currency_stock = [
                {"stock": stock_data["symbol"], "price": stock_data["open"]} for stock_data in response["data"]
            ]
            return currency_stock
        else:
            raise requests.HTTPError(response.status_code)
    else:
        raise Exception("Неверные настройки")


def get_currency_rates():
    """Получаем актуальные курсы валют к рублю"""
    with open(PATH_TO_JSON_SETTINGS) as f:
        user_settings = json.load(f)
    if user_settings["user_currencies"]:
        currencies = ",".join(currency for currency in user_settings['user_currencies'])
        url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={currencies}&base=RUB"
        response = requests.request("GET", url, headers=headers, data={})
        if response.status_code == 200:
            response = response.json()
            currency_rates = [{"currency": k, "rate": v} for k,v in response["rates"].items()]
            return currency_rates
        else:
            raise requests.HTTPError(response.status_code)
    else:
        raise Exception("Неверные настройки")