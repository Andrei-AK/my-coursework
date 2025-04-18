from datetime import datetime
from typing import Optional
import pandas as pd
from dateutil.relativedelta import relativedelta

from src.decirators import write_logs


@write_logs
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Формирует траты по заданной категории за последние три месяца (от переданной даты)"""
    try:
        if date:
            end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        else:
            end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        start_date = end_date - relativedelta(months=3)
        transactions = transactions[
            (transactions["Сумма платежа"] < 0)
            & (transactions["Категория"] == category)
            & (transactions["Дата операции"] > start_date)
            & (transactions["Дата операции"] <= end_date)
        ]
        expenses_of_category = transactions[["Дата операции", "Категория", "Сумма платежа"]].sort_values(["Дата операции"])
        expenses_of_category = expenses_of_category.to_dict()
        return expenses_of_category
    except ValueError:
        print(ValueError)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
