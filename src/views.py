from datetime import datetime as dt
from datetime import time as t
import pandas as pd
from dateutil.relativedelta import relativedelta
from src.decirators import json_write, write_logs


@write_logs
def welcome_time():
    """Выдаем приветствие в зависимости от текущего времени"""
    now_time = dt.now().time()
    if t(23, 0, 0) < now_time or now_time <= t(4, 0, 0):
        message = "Доброй ночи"
    elif t(4, 0, 0) < now_time <= t(11, 0, 0):
        message = "Доброе утро"
    elif t(11, 0, 0) < now_time <= t(17, 0, 0):
        message = "Добрый день"
    else:
        message = "Добрый вечер"
    return message


def get_cashback(transactions, date=None):
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


@write_logs
def get_expenses(transactions: pd.DataFrame) -> dict:
    """Обрабатываем DataFrame и формируем словарь с выборкой"""
    result = {"expenses": {"total_amount": "", "main": ""}, "transfers_and_cash": ""}
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
    result["expenses"]["total_amount"] = total_expenses
    result["expenses"]["main"] = result_category
    result["transfers_and_cash"] = transfers_and_cash
    return result
