import os

from common_func import read_by_pandas, write_json
from src.reports import spending_by_category
from views import welcome_time, get_cashback, get_expenses
from services import change_best_cashback

from dotenv import load_dotenv

load_dotenv()
PATH_TO_DATA = os.getenv("PATH_TO_DATA")
PATH_TO_JSON = os.getenv("PATH_TO_JSON")

main_page = {"greeting": "", "cards": ""}

transactions = read_by_pandas(PATH_TO_DATA)

# Главная
welcome_message = welcome_time()
user_change_date = input("Введите дату в формате YYYY-MM-DD HH:MM:SS:")
cashback = get_cashback(transactions, user_change_date)
main_page["greeting"] = welcome_message
main_page["cards"] = cashback

fp = PATH_TO_JSON + "json_main_page.json"
json_main_page = write_json(fp, main_page)

# События
fp = PATH_TO_JSON + "json_main_page_expenses.json"
expenses = get_expenses(transactions)
json_expenses = write_json(fp, expenses)

# Сервисы
user_change_year = input("Введите год:")
user_change_month = input("Введите месяц:")
best_cashback = change_best_cashback(transactions, user_change_year, user_change_month)
fp = PATH_TO_JSON + "json_services_page.json"
json_services = write_json(fp, best_cashback)

# Отчеты
user_change_categoty = input("Введите категорию:")
user_change_date = input("Введите дату в формате YYYY-MM-DD HH:MM:SS:")
spend_by_category = spending_by_category(transactions, user_change_categoty, user_change_date)
fp = PATH_TO_JSON + "json_reports_page.json"
json_reports = write_json(fp, spend_by_category)
