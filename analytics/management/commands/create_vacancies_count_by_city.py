from django.core.management.base import BaseCommand
from django.db.models import Count
from analytics.models import Vacancy, VacanciesCountByCity


class Command(BaseCommand):
    help = 'Calculate and load VacanciesCountByCity statistics into the database'

    def handle(self, *args, **kwargs):
        self.calculate_vacancy_count_by_city_statistics()
        self.stdout.write(self.style.SUCCESS('VacanciesCountByCity statistics calculated and loaded successfully'))

    def calculate_vacancy_count_by_city_statistics(self):
        VacanciesCountByCity.objects.all().delete()
        bd = Vacancy.objects.all()

        if bd:
            bd = bd.values('area_name')
            bd = bd.annotate(count=Count('id'))
            bd = bd.order_by('-count')

        for row in bd:
            VacanciesCountByCity.objects.create(
                area_name=row['area_name'],
                count=row['count']
            )
