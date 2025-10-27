import datetime
import json
import logging
import os

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
root_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_file_path = os.path.join(str(root_dir_path), "logs", "utils.log")
file_handler = logging.FileHandler(str(log_file_path), "w", encoding="UTF-8")
file_formatter = logging.Formatter("%(asctime)s | %(filename)s:%(lineno)d – %(levelname)s | %(funcName)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

operations_file_path = os.path.join(str(root_dir_path), "data", "operations.xlsx")
user_settings_file_path = os.path.join(str(root_dir_path), "user_settings.json")


def greeting() -> str:
    """Приветствие в формате «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи»
    в зависимости от текущего времени суток."""

    current_hour = datetime.datetime.now().hour
    greeting_messages = ["Доброй ночи", "Доброе утро", "Добрый день", "Добрый вечер"]
    if 0 <= current_hour < 6:
        greeting_message = greeting_messages[0]
    elif 6 <= current_hour < 12:
        greeting_message = greeting_messages[1]
    elif 12 <= current_hour < 18:
        greeting_message = greeting_messages[2]
    else:
        greeting_message = greeting_messages[3]
    logger.info("Сформировано сообщение приветствия.")
    return greeting_message


def reader_excel(path: str = str(operations_file_path)) -> pd.DataFrame:
    """Принимает путь к Excel-файлу и возвращает данные в DataFrame"""

    data = pd.DataFrame()
    try:
        data = pd.read_excel(path, keep_default_na=False)
        logger.info("Excel-файл успешно открыт.")
    except FileNotFoundError as error:
        data = pd.DataFrame()
        logger.error(f"Ошибка: {error}. Дальше передана пустая база данных.")
    finally:
        return data


def current_month_operations(operations: pd.DataFrame, final_datetime: str) -> pd.DataFrame:
    """Принимает данные операций и возвращает только те,
    которые выполнены в месяце входящей даты до дня входящей даты"""

    filtered_operations = pd.DataFrame()
    try:
        final_datetime_dt = datetime.datetime.strptime(final_datetime, "%Y-%m-%d %H:%M:%S")
        logger.info("Формат входной даты соответствует ожидаемому.")
        initial_datetime = datetime.datetime(day=1, month=final_datetime_dt.month, year=final_datetime_dt.year)
        try:
            operations["Дата операции"] = pd.to_datetime(operations["Дата операции"], format="%d.%m.%Y %H:%M:%S")
            filtered_operations = operations.loc[
                (initial_datetime <= operations["Дата операции"]) & (operations["Дата операции"] <= final_datetime)
            ]
            logger.info(f"База отфильтрована для периода {initial_datetime} - {final_datetime_dt}.")
        except KeyError as error:
            logger.error(f"Ошибка: {error}. Дальше передана пустая база данных.")
    except ValueError as error:
        logger.error(f"Ошибка: {error}. Дальше передана пустая база данных.")
    finally:
        return filtered_operations


def cards_info(operations: pd.DataFrame) -> list:
    """Принимает данные операций и выводит:
    - последние 4 цифры карты;
    - общая сумма расходов;
    - кешбэк (1 рубль на каждые 100 рублей - в процентах)"""

    pd.options.mode.copy_on_write = True
    cards = []
    try:
        for column in ["Сумма платежа", "Кэшбэк"]:
            operations[column] = pd.to_numeric(operations[column])
            operations.fillna(value={column: 0}, inplace=True)
        sum_payment_and_cashback_by_card_number = operations.groupby("Номер карты").agg(
            {"Сумма платежа": "sum", "Кэшбэк": "sum"}
        )
        for index, row in sum_payment_and_cashback_by_card_number.iterrows():
            last_digits = str(index).replace("*", "")
            total_spent = round(float((-row["Сумма платежа"])), 2)
            cashback_percent = round(float(row["Кэшбэк"] / 100), 2)
            cards.append({"last_digits": last_digits, "total_spent": total_spent, "cashback": cashback_percent})
        logger.info("Сводная информация по картам сформирована успешно.")
    except KeyError as error:
        logger.error(f"Ошибка: {error}. Дальше передан пустой список.")
    finally:
        return cards


def top_5_operations(operations: pd.DataFrame) -> list[dict]:
    """Выводит топ 5 операций по платежам"""

    top_5_operations_list = []
    try:
        rows_count = operations.shape[0]
        operations_sorted_by_payment = operations.sort_values(
            by="Сумма платежа", ascending=False, key=lambda x: abs(x)
        )
        top_5_operations_sorted_by_payment = operations_sorted_by_payment.iloc[: min(rows_count, 5), :]
        top_5_operations_sorted_by_date = top_5_operations_sorted_by_payment.sort_values(
            by="Дата операции", ascending=False
        )
        for index, row in top_5_operations_sorted_by_date.iterrows():
            date = row["Дата операции"].strftime("%d.%m.%Y")
            amount = row["Сумма платежа"]
            category = row["Категория"]
            description = row["Описание"]
            top_5_operations_list.append(
                {"date": date, "amount": amount, "category": category, "description": description}
            )
        logger.info("Информация по топ-5 операциям сформирована успешно.")
    except KeyError as error:
        logger.error(f"Ошибка: {error}. Дальше передан пустой список.")
    except AttributeError as error:
        logger.error(f"Ошибка: {error}. Дальше передан пустой список.")
    finally:
        return top_5_operations_list


def get_user_settings(user_settings: str, file_path: str = str(user_settings_file_path)) -> list[str]:
    """Извлекает запрашиваемые данные из файла 'user_settings.json'"""

    chosen_user_settings = []
    try:
        with open(file_path) as file:
            user_currencies_stocks = json.load(file)
            logger.info("Файл с данными пользователя успешно открыт.")
            try:
                chosen_user_settings = list(user_currencies_stocks[user_settings])
                logger.info(f"Данные пользователя '{user_settings}' успешно извлечены из файла.")
            except KeyError as error:
                logger.error(f"Ошибка: {error}. По данным пользователя '{user_settings}' передан пустой список.")
    except FileNotFoundError as error:
        logger.error(f"Ошибка: {error}. По данным пользователя '{user_settings}' передан пустой список.")
    finally:
        return chosen_user_settings


def currency_rates(user_currencies: list[str]) -> list[dict]:
    """Выводит список словарей с курсами валют пользователя из API ЦБ РФ"""

    url = "https://www.cbr-xml-daily.ru//daily_json.js"
    response = requests.get(url)
    currency_rates_list = []
    if response.status_code == 200:
        logger.info(f"Данные успешно получены из {url} .")
        for currency in user_currencies:
            value = ""
            try:
                value = response.json()["Valute"][currency]["Value"]
                logger.info(f"Данные по валюте '{currency}' успешно получены.")
            except KeyError as error:
                logger.error(f"Ошибка по валюте '{currency}': {error}.")
            currency_rate = {"currency": currency, "rate": value}
            currency_rates_list.append(currency_rate)
    else:
        logger.error(f"Не удалось получить данные из {url}. Код статуса: {response.status_code}")
        for currency in user_currencies:
            currency_rate = {"currency": currency, "rate": ""}
            currency_rates_list.append(currency_rate)
    return currency_rates_list


def stock_prices(user_stocks: list[str]) -> list[dict]:
    """Выводит стоимость акций"""

    url = "https://www.alphavantage.co/query"
    API_KEY = os.getenv("API_KEY")
    stocks_list = []
    for stock in user_stocks:
        params = {"function": "GLOBAL_QUOTE", "symbol": stock, "apikey": API_KEY}
        response = requests.get(url, params=params)
        price = ""
        if response.status_code == 200:
            try:
                response_dict = response.json()
                price = response_dict["Global Quote"]["05. price"]
                logger.info(f"Данные для '{stock}' успешно получены из {url} .")
            except KeyError as error:
                logger.error(f"Ошибка при выводе данных {stock}: {error}.")
        stock_price = {"stock": stock, "price": price}
        stocks_list.append(stock_price)
    return stocks_list
