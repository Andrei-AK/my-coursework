import json
import logging
import os

from dotenv import load_dotenv

load_dotenv()
PATH_TO_JSON = os.getenv("PATH_TO_JSON")


def write_logs(func):
    def wrapper(*args, **kwargs):
        file_handler = logging.FileHandler(os.path.join("../logs", func.__name__ + ".log"), "w", "UTF-8")
        logging.basicConfig(level="DEBUG", encoding="UTF-8", handlers=[file_handler])
        file_formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
        file_handler.setFormatter(file_formatter)
        logger = logging.getLogger()
        logger.addHandler(file_handler)
        logger.debug(f"Функция {func.__name__} начала работу")
        result = func(*args, **kwargs)
        logger.debug(f"Функция {func.__name__} завершила работу")
        return result

    wrapper.__name__ = func.__name__
    return wrapper


def json_write(func):
    def wrapper(*args, **kwargs):
        if func.__name__ == "get_expenses":
            file_name = "expenses"
        elif func.__name__ == "change_best_cashback":
            file_name = "best_cashback"
        else:
            file_name = func.__name__
        file = PATH_TO_JSON + file_name + ".json"
        func_result = func(*args, **kwargs)
        with open(file, "w", encoding="UTF-8") as fp:
            return json.dump(func_result, fp, indent=4, ensure_ascii=False)

    wrapper.__name__ = func.__name__
    return wrapper
