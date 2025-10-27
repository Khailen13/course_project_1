from src.reports import spending_by_category
from src.services import main as services_main
from src.views import main as views_main
from utils import reader_excel

if __name__ == "__main__":

    # модуль views.py
    date_for_views = input("Для отображения операций месяца введите\nконечную дату и время в формате 'd.m.Y H:M:S': ")
    print(views_main(date_for_views))

    operations = reader_excel()  # чтение файла ./data/operations.xlsx

    # модуль services.py
    data = operations.to_dict()
    year = input("Для вывода информации по кэшбэку введите\n- год: ")
    month = input("- месяц (1-12): ")
    print(services_main(data, int(year), int(month)))

    # модуль reports.py
    category = input(
        "Для получения данных операций по заданной\nкатегории за последние три месяца введите\n- категорию: "
    )
    date = input("- дату в формате 'd.m.Y H:M:S: ")
    print(spending_by_category(operations, category, date))
