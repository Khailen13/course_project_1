import json
import logging
import os

import pandas as pd

logger = logging.getLogger(__name__)
root_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_file_path = os.path.join(str(root_dir_path), "logs", "services.log")
user_settings_file_path = os.path.join(str(root_dir_path), "utils.log")
file_handler = logging.FileHandler(str(log_file_path), "w", encoding="UTF-8")
file_formatter = logging.Formatter("%(asctime)s | %(filename)s:%(lineno)d – %(levelname)s | %(funcName)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def operations_filtered_by_month_and_year(data: pd.DataFrame, year: int, month: int) -> pd.DataFrame:
    """Фильтрует операции по месяцу и году"""

    filtered_operations = pd.DataFrame()
    try:
        data["Дата операции"] = pd.to_datetime(data["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        filtered_operations = data.loc[
            (data["Дата операции"].dt.year == year) & (data["Дата операции"].dt.month == month)
        ]
        logger.info(f"База успешно отфильтрована для месяца {month} {year} года.")
    except KeyError as error:
        logger.error(f"Ошибка в ключе: {error}. Дальше передана пустая база данных.")
    finally:
        return filtered_operations


def cashback_info(operations: pd.DataFrame) -> dict:
    """Выдает количество кэшбэка по категориям"""

    pd.options.mode.copy_on_write = True
    category_cashback_info = {}
    try:
        operations["Кэшбэк"] = pd.to_numeric(operations["Кэшбэк"])
        operations.fillna(value={"Кэшбэк": 0}, inplace=True)
        grouped_operations = operations.groupby("Категория").agg({"Кэшбэк": "sum"})
        for index, row in grouped_operations.iterrows():
            if row["Кэшбэк"] > 0:
                category_cashback_info[index] = float(row["Кэшбэк"])
        logger.info("Сводная информация по кэшбэку сформирована успешно.")
    except KeyError as error:
        logger.error(f"Ошибка в ключе: {error}. Дальше передана пустая база данных.")
    finally:
        return category_cashback_info


def main(data: pd.DataFrame, year: int, month: int) -> str:
    """Выдает информацию по кэшбэку для указанного месяца года в виде json-строки"""

    filtered_operations = operations_filtered_by_month_and_year(data, year=year, month=month)
    category_cashback_info = cashback_info(filtered_operations)
    category_cashback_info_json = json.dumps(category_cashback_info, indent=4, ensure_ascii=False)
    return category_cashback_info_json
