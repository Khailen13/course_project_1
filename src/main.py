from typing import Optional

import pandas as pd

from src.reports import decorator_file_saver, spending_by_category
from src.services import main as services_main
from src.views import main as views_main


def views(final_datetime: str) -> str:
    """Принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS и отдает корректный JSON-ответ"""

    answer_json = views_main(final_datetime)
    return answer_json


def services(data: list[dict], year: int, month: int) -> str:
    """Выдает информацию по кэшбэку для указанного месяца года в виде json-строки"""

    category_cashback_info_json = services_main(data, year, month)
    return category_cashback_info_json


@decorator_file_saver("reports.xlsx")
def reports(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца (от переданной даты)
    Формат входной даты '%d.%m.%Y %H:%M:%S'.
    Декоратор сохраняет полученные данные в Excel-файл в папку data с именем указанным в аргументе.
    """

    return spending_by_category(transactions, category, date)
