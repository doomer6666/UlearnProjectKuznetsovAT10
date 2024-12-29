import re
from collections import Counter
from django.core.management.base import BaseCommand
from analytics.models import Vacancy, Skill

class Command(BaseCommand):
    help = 'Calculate and load Skill statistics into the database'

    def handle(self, *args, **kwargs):
        Skill.objects.all().delete()

        vacancies = Vacancy.objects.all()
        skills_by_year = {}

        for vacancy in vacancies:
            year = vacancy.published_at.year
            skills = re.split(r',|\s*\n\s*|\s*;\s*|\s*\|\s*', vacancy.key_skills)

            if year not in skills_by_year:
                skills_by_year[year] = []

            skills_by_year[year].extend([skill.strip() for skill in skills if skill.strip()])

        top_skills_by_year = {}

        for year, skills in skills_by_year.items():
            if skills:  # Проверяем, есть ли навыки для данного года
                skill_counts = Counter(skills)  # Подсчет частоты навыков
                top_skills = skill_counts.most_common(21)
                top_skills = top_skills[1:]  # Убираем первый мусорный элемент с общим количеством
                top_skills_by_year[year] = top_skills

        # Исключаем годы без навыков и сохраняем данные в модель Skill
        for year, skills in top_skills_by_year.items():
            if skills:
                for skill, count in skills:
                    Skill.objects.create(year=year, name=skill, count=count)

        self.stdout.write(self.style.SUCCESS('Skill created and saved successfully'))
