from django.core.management.base import BaseCommand
from django.db.models import Count
from analytics.models import Vacancy, VacanciesCountByYear

class Command(BaseCommand):
    help = 'Calculate and load vacancy count statistics into the database'

    def handle(self, *args, **kwargs):
        self.calculate_vacancy_count_statistics()
        self.stdout.write(self.style.SUCCESS('Vacancy count statistics calculated and loaded successfully'))

    def calculate_vacancy_count_statistics(self):
        VacanciesCountByYear.objects.all().delete()
        data = Vacancy.objects.all()

        # Рассчитываем количество вакансий по годам
        vacancy_counts = (
            data.values('published_at__year')
            .annotate(count=Count('id'))
            .order_by('published_at__year')
        )

        for count in vacancy_counts:
            VacanciesCountByYear.objects.create(
                year=count['published_at__year'],
                count=count['count']
            )
