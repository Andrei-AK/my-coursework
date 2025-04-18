import os
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta

from src.decirators import write_logs


@write_logs
def change_best_cashback(transactions, year, month):
    """Анализ выгодности категорий повышенного кешбэка за выбранный месяц."""
    start_date = datetime(int(year), int(month), 1, 0, 0, 0)
    end_date = start_date + relativedelta(months=1)
    category_cashback = transactions[
        (transactions["Кэшбэк"] > 0)
        & (pd.notna(transactions["Кэшбэк"]))
        & (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] < end_date)
    ]
    category_cashback = (
        category_cashback.groupby("Категория")["Кэшбэк"].sum().reset_index().sort_values(["Кэшбэк"], ascending=False)
    )
    category_cashback = category_cashback.iloc[:3]
    category_cashback = category_cashback.set_index("Категория")["Кэшбэк"].to_dict()
    return category_cashback
