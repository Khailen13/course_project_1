import datetime
import logging
import os
from typing import Optional

import pandas as pd
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)
root_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_file_path = os.path.join(str(root_dir_path), "logs", "reports.log")
file_handler = logging.FileHandler(str(log_file_path), "w", encoding="UTF-8")
file_formatter = logging.Formatter("%(asctime)s | %(filename)s:%(lineno)d – %(levelname)s | %(funcName)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def decorator_file_saver(file_name: str):
    def my_decorator(func):
        def wrapper(*args, **kwargs):
            file_path = os.path.join(str(root_dir_path), "data", file_name)
            func(*args, **kwargs).to_excel(file_path)
            return func(*args, **kwargs)

        return wrapper

    return my_decorator


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)
    Формат входной даты '%d.%m.%Y %H:%M:%S'"""

    filtered_transactions = pd.DataFrame()
    try:
        end_of_period = datetime.datetime.strptime(date, "%d.%m.%Y %H:%M:%S") if date else datetime.datetime.now()

        start_of_period = end_of_period + relativedelta(months=-3)
        transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S")
        filtered_transactions = transactions.loc[
            (start_of_period <= transactions["Дата операции"])
            & (transactions["Дата операции"] <= end_of_period)
            & (transactions["Категория"] == category)
        ]
        logger.info(f"Данные отфильтрованы по категории '{category}' за период {start_of_period} - {end_of_period}.")
    except ValueError as error:
        logger.error(f"Ошибка: {error}. Сгенерирована пустая база данных.")
    except KeyError as error:
        logger.error(f"Ошибка в ключе: {error}. Сгенерирована пустая база данных.")
    finally:
        return filtered_transactions
