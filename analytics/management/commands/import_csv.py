# analytics/management/commands/import_csv.py

import csv
from django.core.management.base import BaseCommand
from analytics.models import Vacancy
from datetime import datetime


class Command(BaseCommand):
    help = 'Import data from a CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to import')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        try:
            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)  # Используем DictReader для удобства
                for row in reader:
                    # Конвертация даты из строки в объект datetime
                    published_at = datetime.strptime(row['published_at'], '%Y-%m-%dT%H:%M:%S%z')

                    # Создание или обновление записи в базе данных
                    Vacancy.objects.update_or_create(
                        name=row['name'],
                        defaults={
                            'key_skills': row['key_skills'],
                            'salary_from': float(row['salary_from']) if row['salary_from'] else None,
                            'salary_to': float(row['salary_to']) if row['salary_to'] else None,
                            'salary_currency': row['salary_currency'],
                            'area_name': row['area_name'],
                            'published_at': published_at,
                        }
                    )
                self.stdout.write(self.style.SUCCESS('Данные успешно импортированы!'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка при импорте: {e}'))
