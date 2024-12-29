from django.core.management.base import BaseCommand
from analytics.models import VacanciesCountByCity
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

class Command(BaseCommand):
    help = 'Create and save a VacanciesCountByCity plot'

    def handle(self, *args, **kwargs):
        create_vacancies_pie_plot()
        self.stdout.write(self.style.SUCCESS('VacanciesCountByCity plot created and saved successfully'))


def create_vacancies_pie_plot():

    # Получаем данные из базы данных
    vacancies_by_city = list(VacanciesCountByCity.objects.all().values('area_name', 'count'))

    # Преобразуем данные в DataFrame для удобства работы
    df = pd.DataFrame(vacancies_by_city)

    # Создаем график
    fig, ax = plt.subplots(figsize=(10, 6))  # Устанавливаем размер графика
    plot_city_vacancy_percentages(df, ax)

    # Сохраняем график с установленными границами
    plt.tight_layout()
    plt.savefig('analytics/static/img/vacancies_count_by_city_plot.png')
    plt.show()


def plot_city_vacancy_percentages(df, ax):
    # Подсчитываем процент вакансий по городам
    df['percentage'] = (df['count'] / df['count'].sum()) * 100

    # Разделяем данные на те, которые >= 1% и остальные
    labels = []
    sizes = []
    for index, row in df.iterrows():
        if row['percentage'] >= 1:
            labels.append(f"{row['area_name']} ({row['percentage']:.1f}%)")
            sizes.append(row['percentage'])
        else:
            if "Остальные" in labels:
                sizes[labels.index("Остальные")] += row['percentage']
            else:
                labels.append("Остальные")
                sizes.append(row['percentage'])

    # Создаем круговую диаграмму
    ax.pie(sizes, labels=labels, textprops={'fontsize': 6})
    ax.set_title('Доля вакансий по городам', fontsize=8)
