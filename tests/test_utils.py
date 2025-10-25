import datetime
from unittest.mock import Mock, mock_open, patch

import pandas as pd
import pytest

from src.utils import (cards_info, currency_rates, current_month_operations, get_user_settings, greeting, reader_excel,
                       stock_prices, top_5_operations)

pd.options.mode.copy_on_write = True


@pytest.mark.parametrize(
    "hour, message", [(0, "Доброй ночи"), (6, "Доброе утро"), (12, "Добрый день"), (18, "Добрый вечер")]
)
def test_greeting(hour, message):
    """Проверка приветствия в зависимости от времени суток"""

    real_datetime = datetime.datetime.now()
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = real_datetime.replace(hour=hour)
        assert greeting() == message


def test_reader_excel():
    """Проверка вывода данных при наличии файла"""

    mock_data = [{"Col_1": 11, "Col_2": 12}]
    expected_df = pd.DataFrame([[11, 12]], columns=["Col_1", "Col_2"]).to_dict(orient="records")
    with patch("pandas.read_excel") as mock_excel_reader:
        mock_excel_reader.return_value = mock_data
        result = reader_excel()
        assert result == expected_df


def test_reader_excel_file_not_found_error():
    """Проверка при отсутствии файла"""

    assert reader_excel("non-existent_file").empty


def test_current_month_incorrect_date(operations):
    """Проверка при неправильном формате входящих даты и времени"""

    final_datetime = "01.12.2021 13:15:00"
    assert current_month_operations(operations, final_datetime).empty


def test_current_month_key_error(operations):
    """Проверка при отсутствии ключа 'Дата операции'"""

    final_datetime = "2021-12-01 13:15:00"
    df_without_the_required_key = operations.rename(columns={"Дата операции": "Ошибочный ключ"})
    assert current_month_operations(df_without_the_required_key, final_datetime).empty


def test_current_month_success(operations):
    """Проверка успешной фильтрации операций"""

    final_datetime = "2021-12-01 13:15:00"
    expected_df = operations.iloc[[7, 8], :]
    expected_df["Дата операции"] = pd.to_datetime(expected_df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    assert current_month_operations(operations, final_datetime).equals(expected_df)


def test_cards_info_key_error(operations):
    """Проверка при отсутствии ключей 'Сумма платежа' или 'Кэшбэк'"""

    operations = operations.rename(columns={"Сумма платежа": "Ошибочный ключ 1", "'Кэшбэк": "Ошибочный ключ 2"})
    assert len(cards_info(operations)) == 0


def test_cards_info_success(operations):
    """Проверка успешной работы функции"""

    expected_result = [
        {"last_digits": "5091", "total_spent": 5522.2, "cashback": 0.25},
        {"last_digits": "7197", "total_spent": 1033.73, "cashback": 0.15},
    ]
    assert cards_info(operations) == expected_result


def test_get_user_settings_file_not_found_error():
    """Проверка при отсутствии файла"""

    assert get_user_settings("user_currencies", "Неверный путь к файлу") == []


def test_top_5_operations_until_2021_12_03(operations, top_5_operations_until_2021_12_03):
    """Проверка топ 5 операций по платежам до 2021-12-03 00:00:00 - в рассматриваемой базе более 5 операций"""

    final_datetime = "2021-12-03 00:00:00"
    considered_operations = current_month_operations(operations, final_datetime)
    assert top_5_operations(considered_operations) == top_5_operations_until_2021_12_03


def test_top_5_operations_until_2021_12_02(operations, top_5_operations_until_2021_12_02):
    """Проверка топ 5 операций по платежам до 2021-12-02 00:00:00 - в рассматриваемой базе менее 5 операций"""

    final_datetime = "2021-12-02 00:00:00"
    considered_operations = current_month_operations(operations, final_datetime)
    assert top_5_operations(considered_operations) == top_5_operations_until_2021_12_02


def test_top_5_operations_until_2021_12_01(operations):
    """Проверка при пустой базе"""

    final_datetime = "2021-12-01 00:00:00"
    considered_operations = current_month_operations(operations, final_datetime)
    assert top_5_operations(considered_operations) == []


def test_top_5_operations_key_error(operations):
    """Проверка при несоответствии иен столбцов 'Номер карты', 'Дата операции', 'Сумма платежа', 'Кэшбэк'"""

    final_datetime = "2021-12-03 00:00:00"
    considered_operations = current_month_operations(operations, final_datetime)
    data_with_incorrect_names = considered_operations.rename(
        columns={
            "Номер карты": "Ошибочный ключ 1",
            "Дата операции": "Ошибочный ключ 2",
            "Сумма платежа": "Ошибочный ключ 3",
            "Кэшбэк": "Ошибочный ключ 4",
        }
    )
    assert top_5_operations(data_with_incorrect_names) == []


def test_top_5_operations_attribute_error(operations):
    """Проверка при несоответствии данных столбца 'Дата операции' объекту datetime"""

    assert top_5_operations(operations) == []


def test_get_user_settings_key_error(user_settings):
    """Проверка при ошибочном ключе данных"""

    mock_data = mock_open(read_data=user_settings)
    with patch("builtins.open", mock_data):
        assert get_user_settings("user_products", "mock_data") == []


def test_get_user_settings_success(user_settings):
    """Проверка успешного выполнения"""

    mock_data = mock_open(read_data=user_settings)
    with patch("builtins.open", mock_data):
        assert get_user_settings("user_currencies", "mock_data") == ["USD", "EUR"]


def test_currency_rates_success(some_currency_rates):
    """Проверка успешного выполнения"""

    user_currencies = ["USD", "EUR"]
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = some_currency_rates
    with patch("requests.get", return_value=mock_response):
        result = currency_rates(user_currencies)
        assert result == [{"currency": "USD", "rate": 80.9713}, {"currency": "EUR", "rate": 94.082}]


def test_currency_rates_request_error(some_currency_rates):
    """Проверка при ошибке запроса"""

    user_currencies = ["USD", "EUR"]
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = some_currency_rates
    with patch("requests.get", return_value=mock_response):
        result = currency_rates(user_currencies)
        assert result == [{"currency": "USD", "rate": ""}, {"currency": "EUR", "rate": ""}]


def test_currency_rates_valute_absence(some_currency_rates):
    """Проверка при отсутствии валюты"""

    user_currencies = ["Valute_1", "Valute"]
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = some_currency_rates
    with patch("requests.get", return_value=mock_response):
        result = currency_rates(user_currencies)
        assert result == [{"currency": user_currencies[0], "rate": ""}, {"currency": user_currencies[1], "rate": ""}]


def test_stock_prices_success(stock):
    """Проверка успешного выполнения"""

    user_stocks = ["AAPL"]
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = stock
    with patch("requests.get", return_value=mock_response):
        result = stock_prices(user_stocks)
        assert result == [{"stock": "AAPL", "price": "259.5800"}]


def test_stock_prices_request_error(stock):
    """Проверка при ошибке запроса"""

    user_stocks = ["AAPL"]
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.json.return_value = stock
    with patch("requests.get", return_value=mock_response):
        result = stock_prices(user_stocks)
        assert result == [{"stock": "AAPL", "price": ""}]
