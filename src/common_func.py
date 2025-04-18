import json

import pandas as pd

from src.decirators import write_logs


@write_logs
def read_by_pandas(file_path, datatime_to_timestamp: bool = True):
    """excel to list"""
    file_data = pd.read_excel(file_path)
    file_data["Дата операции"] = pd.to_datetime(file_data["Дата операции"], dayfirst=True)
    return file_data


@write_logs
def write_json(path_file, json_data):
    with open(path_file, "w", encoding="UTF-8") as f:
        result = json.dump(json_data, f, indent=4, ensure_ascii=False)
        return result
