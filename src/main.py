import os
from pathlib import Path

from common_func import read_by_pandas, write_json
from src.reports import spending_by_category
from views import welcome_time, get_cashback, get_expenses, get_incomes, get_currency_rates, get_currency_stock
from services import change_best_cashback

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).parent.parent
PATH_TO_DATA = BASE_DIR / os.getenv("PATH_TO_DATA")
PATH_TO_JSON = BASE_DIR / os.getenv("PATH_TO_JSON")

views_main = {"greeting": "", "cards": "", "currency_rates": "", "stock_prices": ""}
views_events = {"expenses": "", "income": "", "currency_rates": "", "stock_prices": ""}


transactions = read_by_pandas(PATH_TO_DATA)

# # Главная
#
# rates = get_currency_rates()
# stock = get_currency_stock()
#
# welcome_message = welcome_time()
# user_change_date = input("Введите дату в формате YYYY-MM-DD HH:MM:SS")
# cashback = get_cashback(transactions, user_change_date)
# views_main["greeting"] = welcome_message
# views_main["cards"] = cashback
# views_main["currency_rates"] = rates
# views_main["stock_prices"] = stock
# fp = PATH_TO_JSON + "json_views_main.json"
# write_json(fp, views_main)
#
# # События
# expenses = get_expenses(transactions)
# incomes = get_incomes(transactions, "2021-11-30 00:00:00", "2")
# views_events["expenses"] = expenses
# views_events["income"] = incomes
# views_events["currency_rates"] = rates
# views_events["stock_prices"] = stock
# fp = PATH_TO_JSON + "json_views_events.json"
# write_json(fp, views_events)

#Сервисы
user_change_year = input("Введите год:")
user_change_month = input("Введите месяц:")
best_cashback = change_best_cashback(transactions, user_change_year, user_change_month)
fp = PATH_TO_JSON + "json_services_page.json"
write_json(fp, best_cashback)

# # Отчеты
# user_change_category = input("Введите категорию:")
# user_change_date = input("Введите дату в формате YYYY-MM-DD HH:MM:SS:")
# spend_by_category = spending_by_category(transactions, user_change_category, user_change_date)
# fp = PATH_TO_JSON + "json_reports_page.json"
# write_json(fp, spend_by_category)
