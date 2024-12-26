import pandas as pd
from time import sleep
import requests
from django.core.management import BaseCommand
from django.db import IntegrityError
from analytics.models import Vacancy, Currency


def get_exchange_rates(date, salary_currency, max_retries=3, delay=5):
    '''
    Достаёт по api информацию с сервера
    :param date: интересующая нас дата
    :param salary_currency: кодовое имя валюты
    :param max_retries: максимальное количество попыток
    :param delay: задержка между попытками
    :return: курс валюты на запрошенную дату
    '''
    date_str = date.strftime('%d/%m/%Y')
    url = f"http://www.cbr.ru/scripts/XML_daily.asp?date_req={date_str}"  # Формируем URL для запроса с указанной датой

    for attempt in range(max_retries):
        try:
            data = pd.read_xml(url, encoding="windows-1251")  # Загружаем и парсим XML данные с сайта ЦБ
            if salary_currency != "BYR":
                currency = float(data[data['CharCode'] == salary_currency]['Value'].values[0].replace(',', '.')) if not \
                data[data['CharCode'] == salary_currency].empty else 0
            else:
                currency = float(data[data['CharCode'] == "BYR"]['Value'].values[0].replace(',', '.')) if not \
                data[data['CharCode'] == "BYR"].empty else 0
                if currency == 0:
                    currency = float(data[data['CharCode'] == "BYN"]['Value'].values[0].replace(',', '.')) if not \
                    data[data['CharCode'] == "BYN"].empty else 0
            return currency  # Возвращаем курс
        except (requests.ConnectionError, ConnectionResetError) as e:
            if attempt < max_retries - 1:
                sleep(delay)  # Задержка перед повторной попыткой
            else:
                raise e


class Command(BaseCommand):
    help = 'Save exchange rates to the database'

    def handle(self, *args, **options):
        exchange_rates = []
        processed = set()

        data = Vacancy.objects.all()
        total_vacancies = data.count()  # Общее количество вакансий

        for index, item in enumerate(data, start=1):
            self.stdout.write(self.style.NOTICE(f"Processing vacancy {index}/{total_vacancies}"))

            if item.salary_currency and item.salary_currency != 'RUR':
                date = item.published_at.replace(day=1)
                key = (date.strftime('%Y-%m-%d'), item.salary_currency)
                if key not in processed:
                    try:
                        currency = get_exchange_rates(date, item.salary_currency)
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"Error fetching exchange rate for {item.salary_currency} on {date}: {e}"))
                        continue

                    if item.salary_currency:  # Проверяем наличие валюты
                        exchange_rates.append({'date': date, 'currency_code': item.salary_currency, 'currency': currency})
                        processed.add(key)

        # Сохраняем данные в базу данных
        for rate in exchange_rates:
            try:
                Currency.objects.create(
                    date=rate['date'],
                    currency_code=rate['currency_code'],
                    currency=rate['currency']
                )
            except IntegrityError:
                self.stdout.write(self.style.WARNING(f"Duplicate entry for {rate['currency_code']} on {rate['date']}"))

        self.stdout.write(self.style.SUCCESS('Successfully saved exchange rates to the database'))
