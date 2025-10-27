import pandas as pd

from src.reports import spending_by_category


def test_spending_by_category_success(operations):
    """Проверка успешной работы"""

    category = "Супермаркеты"
    date = "02.12.2021 22:00:00"
    expected_data = operations.iloc[[3, 6], :]
    expected_data["Дата операции"] = pd.to_datetime(expected_data["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    assert spending_by_category(operations, category, date).equals(expected_data)


def test_spending_by_category_key_error(operations):
    """Проверка при отсутствии столбца 'Дата операции' или 'Категория'"""

    operations_without_required_columns = operations.rename(
        columns={"Дата операции": "Ошибочный ключ 1", "Категория": "Ошибочный ключ 2"}
    )
    category = "Супермаркеты"
    date = "02.12.2021 22:00:00"
    assert spending_by_category(operations_without_required_columns, category, date).empty


def test_spending_by_category_value_error(operations):
    """Проверка при отсутствии столбца 'Дата операции' или 'Категория'"""

    category = "Супермаркеты"
    date = "2021-12-02 22:00:00"
    assert spending_by_category(operations, category, date).empty
