from django.core.management.base import BaseCommand
from django.db.models import Count, Avg, F
from django.db.models.functions import Round

from analytics.models import Vacancy, SalaryByCity


class Command(BaseCommand):
    help = 'Calculate and load SalaryByCity statistics into the database'

    def handle(self, *args, **kwargs):
        self.calculate_vacancy_count_statistics()
        self.stdout.write(self.style.SUCCESS('SalaryByCity statistics calculated and loaded successfully'))

    def calculate_vacancy_count_statistics(self):
        SalaryByCity.objects.all().delete()
        total_vacancies = Vacancy.objects.filter(area_name__isnull=False).count()
        bd = Vacancy.objects.filter(area_name__isnull=False)

        if bd:
            bd = bd.values('area_name')
            bd = bd.annotate(count_vacancies=Count('area_name'))
            bd = bd.filter(count_vacancies__gt=total_vacancies * 0.01)
            bd = bd.annotate(avg_salary=Round(Avg((F('salary_from') + F('salary_to')) / 2), 1))
            bd = bd.filter(avg_salary__lte=10000000)
            bd = bd.order_by('-avg_salary')

        for row in bd:
            SalaryByCity.objects.create(
                area_name=row['area_name'],
                avg_salary=row['avg_salary']
            )
