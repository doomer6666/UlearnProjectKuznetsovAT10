import csv
import logging
from django.core.management.base import BaseCommand
from analytics.models import Vacancy
from datetime import datetime


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to import')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        # Настройка логгирования
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(__name__)

        keywords = [
            'Системный администратор', 'system admin', 'сисадмин', 'сис админ', 'системный админ', 'cистемный админ',
            'администратор систем', 'системний адміністратор'
        ]

        try:
            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                total_rows = sum(1 for row in reader)
                csvfile.seek(0)  # Возвращаем указатель в начало файла
                reader = csv.DictReader(csvfile)

                imported_rows = 0
                current_row = 0

                for row in reader:
                    current_row += 1
                    if any(keyword.lower() in row['name'].lower() for keyword in keywords):
                        published_at = datetime.strptime(row['published_at'], '%Y-%m-%dT%H:%M:%S%z')
                        Vacancy.objects.create(
                            name=row['name'],
                            defaults={
                                'key_skills': row['key_skills'] if row['key_skills'] else '',
                                'salary_from': float(row['salary_from']) if row['salary_from'] else None,
                                'salary_to': float(row['salary_to']) if row['salary_to'] else None,
                                'salary_currency': row['salary_currency'],
                                'area_name': row['area_name'],
                                'published_at': published_at,
                            }
                        )
                        imported_rows += 1
                        logger.info(f"Вакансия '{row['name']}' успешно импортирована ({current_row}/{total_rows}).")

                self.stdout.write(self.style.SUCCESS(f'Импортировано {imported_rows} из {total_rows} строк.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Ошибка при импорте: {e}'))
            logger.error(f'Ошибка при импорте: {e}')
