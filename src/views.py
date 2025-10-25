import json
import os

from src.utils import (cards_info, currency_rates, current_month_operations, get_user_settings, greeting, reader_excel,
                       stock_prices, top_5_operations, root_dir_path)


def main(final_datetime: str) -> str:
    """Принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS и отдает корректный JSON-ответ"""

    # Сообщение с приветствием
    answer_dict = {}
    answer_dict["greeting"] = greeting()

    # Чтение excel-файла с операциями
    operations = reader_excel()

    # Фильтрация операций по входной дате и времени
    operations_current_month = current_month_operations(operations, final_datetime)

    # Сводная информация по картам
    operations_by_card = cards_info(operations_current_month)
    answer_dict["cards"] = operations_by_card

    # Топ-5 операций по платежам
    answer_dict["top_transactions"] = top_5_operations(operations_current_month)

    # Путь к файлу user_settings.json
    user_settings_file_path = os.path.join(str(root_dir_path), "user_settings.json")

    # Информация по валютам
    user_currencies = get_user_settings("user_currencies", user_settings_file_path)
    answer_dict["currency_rates"] = currency_rates(user_currencies)

    # Информация по акциям
    user_stocks = get_user_settings("user_stocks", user_settings_file_path)
    answer_dict["stock_prices"] = stock_prices(user_stocks)

    # Приведение данных к json-строке
    answer_json = json.dumps(answer_dict, indent=2, ensure_ascii=False)

    return answer_json
