from django.core.management.base import BaseCommand
from analytics.models import Skill
import pandas as pd
from matplotlib import pyplot as plt

class Command(BaseCommand):
    help = 'Create and save skill plots by year'

    def handle(self, *args, **kwargs):
        create_skill_plots()
        self.stdout.write(self.style.SUCCESS('Skill plots created and saved successfully'))


def create_skill_plots():
    # Получаем данные из базы данных
    skills = list(Skill.objects.all().values('year', 'name', 'count'))

    # Преобразуем данные в DataFrame для удобства работы
    df = pd.DataFrame(skills)

    # Группируем данные по годам
    years = df['year'].unique()
    for year in years:
        df_year = df[df['year'] == year]

        # Создаем график
        fig, ax = plt.subplots(figsize=(10, 6))  # Устанавливаем размер графика
        plot_skill_counts(df_year, ax, year)

        # Сохраняем график с установленными границами
        plt.tight_layout()
        plt.savefig(f'static/img/skills_{year}_plot.png')
        plt.close()

def plot_skill_counts(df, ax, year):
    # Сортируем данные по количеству
    df = df.sort_values(by='count', ascending=False)

    # Создаем столбчатую диаграмму
    ax.bar(df['name'], df['count'])
    ax.set_title(f'ТОП навыков за {year} год', fontsize=12)
    ax.set_xlabel('Навык', fontsize=10)
    ax.set_ylabel('Количество', fontsize=10)
    ax.tick_params(axis='x', rotation=90)
