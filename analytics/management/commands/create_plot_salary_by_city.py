from django.core.management.base import BaseCommand
from analytics.models import SalaryByCity
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

class Command(BaseCommand):
    help = 'Create and save a SalaryByCity plot'

    def handle(self, *args, **kwargs):
        create_salary_trend_plot()
        self.stdout.write(self.style.SUCCESS('SalaryByCity plot created and saved successfully'))


def create_salary_trend_plot():

    # Получаем данные из базы данных
    salary_by_city = list(SalaryByCity.objects.all().values('area_name', 'avg_salary'))

    # Преобразуем данные в DataFrame для удобства работы
    df = pd.DataFrame(salary_by_city)

    # Создаем график
    fig, ax = plt.subplots(figsize=(10, 6))  # Устанавливаем размер графика
    plot_yearly_salaries(df, ax)

    # Сохраняем график с установленными границами
    plt.tight_layout()
    plt.savefig('static/img/salary_by_city_plot.png')
    plt.show()


def plot_yearly_salaries(df, ax):
    # Метки для осей
    labels = df['area_name'].tolist()

    x = np.arange(len(labels))
    width = 0.4
    # Строим столбчатую диаграмму
    ax.bar(x, df['avg_salary'], width, label='Средняя з/п')

    # Настройки графика
    ax.set_title('Уровень зарплат по городам', fontsize=8)
    ax.set_xticks(x, labels=labels, rotation=90, fontsize=8)
    ax.tick_params(axis='y', labelsize=8)
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(axis='y')
