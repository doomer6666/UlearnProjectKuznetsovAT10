from django.core.management.base import BaseCommand
from django.db.models import Avg, F
from django.db.models.functions import Round, Substr

from analytics.models import Vacancy, SalaryByYear, Currency


class Command(BaseCommand):
    help = 'Calculate and load salary trends into the database'

    def handle(self, *args, **kwargs):
        self.calculate_salary_trends()
        self.stdout.write(self.style.SUCCESS('Salary trends calculated and loaded successfully'))

    def calculate_salary_trends(self):
        SalaryByYear.objects.all().delete()
        data = Vacancy.objects.all()

        # Преобразуем зарплаты в рубли
        currency_dict = {(item.date.strftime('%Y-%m-%d'), item.currency_code): item.currency for item in Currency.objects.all()}
        for item in data:
            if item.salary_currency and item.salary_currency != 'RUR':
                date = item.published_at.replace(day=1)
                exchange_rate = currency_dict.get((date.strftime('%Y-%m-%d'), item.salary_currency), 0)
                if exchange_rate:
                    item.salary_from = float(item.salary_from or 0) * exchange_rate
                    item.salary_to = float(item.salary_to or 0) * exchange_rate

        # Фильтруем вакансии, чтобы исключить те, у которых зарплата выше 10 миллионов рублей
        data = data.filter(salary_from__lte=10000000, salary_to__lte=10000000)

        # Рассчитываем среднее значение (salary_from + salary_to) / 2
        data = data.annotate(avg_salary=((F('salary_from') + F('salary_to')) / 2))

        # Рассчитываем среднюю зарплату по годам
        salary_trends = (
            data.annotate(year=Substr('published_at', 1, 4))  # Аннотируем данные, извлекая год из даты публикации
            .values('year')  # Группируем данные по годам
            .annotate(avg_salary=Round(Avg('avg_salary'), 2))  # Рассчитываем среднюю зарплату по годам и округляем до 2 знаков после запятой
        )

        for trend in salary_trends:
            SalaryByYear.objects.create(
                year=trend['year'],
                avg_salary=trend['avg_salary']
            )
