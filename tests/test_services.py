import json

from src.services import cashback_info, main, operations_filtered_by_month_and_year


def test_operations_filtered_by_month_and_year_success(operations):
    """Проверка успешной работы"""

    data = operations
    year = 2021
    month = 12
    assert operations_filtered_by_month_and_year(data, year, month).equals(data)
    month = 10
    assert not operations_filtered_by_month_and_year(data, year, month).equals(data)


def test_operations_filtered_by_month_and_year_key_error(operations):
    """Проверка при отсутствии столбца 'Дата операции'"""

    data = operations.rename(columns={"Дата операции": "Ошибочный ключ"})
    year = 2021
    month = 12
    assert operations_filtered_by_month_and_year(data, year, month).empty


def test_cashback_info_success(operations):
    """Проверка успешной работы"""

    expected_result = {"Каршеринг": 25.0, "Супермаркеты": 8.0, "Фастфуд": 6.0, "Дом и ремонт": 1.0}
    assert cashback_info(operations) == expected_result


def test_cashback_info_key_error(operations):
    """Проверка при отсутствии столбца 'Категория' или 'Кэшбэк'"""

    operations_without_required_columns = operations.rename(
        columns={"Категория": "Ошибочный ключ 1", "Кэшбэк": "Ошибочный ключ 2"}
    )
    assert not cashback_info(operations_without_required_columns)


def test_main_success(operations):
    """Проверка успешной работы"""

    year = 2021
    month = 12
    result_dict = {"Дом и ремонт": 1.0, "Каршеринг": 25.0, "Супермаркеты": 8.0, "Фастфуд": 6.0}
    expected_result_json = json.dumps(result_dict, indent=4, ensure_ascii=False)
    assert main(operations, year, month) == expected_result_json
