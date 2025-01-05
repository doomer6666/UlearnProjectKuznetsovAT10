from django.core.management.base import BaseCommand
from analytics.models import VacanciesCountByYear
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

class Command(BaseCommand):
    help = 'Create and save a vacancies count by year trend plot'

    def handle(self, *args, **options):
        create_vac_count_trend_plot()
        self.stdout.write(self.style.SUCCESS('Vacancies count by year trend plot created and saved successfully'))

def create_vac_count_trend_plot():

    # Получаем данные из базы данных
    vac_count_trends = list(VacanciesCountByYear.objects.all().values('year', 'count'))

    # Преобразуем данные в DataFrame для удобства работы
    df = pd.DataFrame(vac_count_trends)

    # Создаем график
    fig, ax = plt.subplots(figsize=(10, 6))  # Устанавливаем размер графика
    plot_yearly_salaries(df, ax)

    # Сохраняем график с разрешением 1000x600 пикселей
    plt.tight_layout()
    plt.savefig('static/img/vac_count_trend_plot.png', dpi=100, bbox_inches='tight')
    plt.show()


def plot_yearly_salaries(df, ax):
    # Метки для осей
    labels = df['year'].tolist()

    x = np.arange(len(labels))
    width = 0.4
    # Строим столбчатую диаграмму
    ax.bar(x, df['count'], width, label='Кол-во вакансий')

    # Настройки графика
    ax.set_title('Кол-во вакансий по годам', fontsize=8)
    ax.set_xticks(x, labels=labels, rotation=90, fontsize=8)
    ax.tick_params(axis='y', labelsize=8)
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(axis='y')
