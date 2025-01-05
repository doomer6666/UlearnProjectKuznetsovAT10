from django.core.management.base import BaseCommand
from analytics.models import SalaryByYear
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

class Command(BaseCommand):
    help = 'Create and save a salary trend plot'

    def handle(self, *args, **kwargs):
        create_salary_trend_plot()
        self.stdout.write(self.style.SUCCESS('Salary trend plot created and saved successfully'))


def create_salary_trend_plot():

    # Получаем данные из базы данных
    salary_trends = list(SalaryByYear.objects.all().values('year', 'avg_salary'))

    # Преобразуем данные в DataFrame для удобства работы
    df = pd.DataFrame(salary_trends)

    # Создаем график
    fig, ax = plt.subplots(figsize=(10, 6))  # Устанавливаем размер графика
    plot_yearly_salaries(df, ax)

    # Сохраняем график с разрешением 1000x600 пикселей
    plt.tight_layout()
    plt.savefig('static/img/salary_trend_plot.png', dpi=100, bbox_inches='tight')
    plt.show()


def plot_yearly_salaries(df, ax):
    # Метки для осей
    labels = df['year'].tolist()

    x = np.arange(len(labels))
    width = 0.4
    # Строим столбчатую диаграмму
    ax.bar(x, df['avg_salary'], width, label='Средняя з/п')

    # Настройки графика
    ax.set_title('Уровень зарплат по годам', fontsize=8)
    ax.set_xticks(x, labels=labels, rotation=90, fontsize=8)
    ax.tick_params(axis='y', labelsize=8)
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(axis='y')
