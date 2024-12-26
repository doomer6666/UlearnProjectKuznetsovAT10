from django.shortcuts import render
from .models import Vacancy
from django.db.models import Avg, Count, F, Q
from datetime import datetime
from collections import Counter
import requests


def index(request):
    return render(request, 'analytics/index.html')


def get_currency_rate(currency, date):
    # Получение курса валют с сайта ЦБ РФ (примерный код)
    response = requests.get(f'https://www.cbr.ru/scripts/XML_daily.asp?date_req={date.strftime("%d/%m/%Y")}')
    # Обработка ответа и извлечение курса валюты
    # (Этот код требует доработки для обработки XML-ответа)


def statistics(request):
    # Получаем все вакансии
    vacancies = Vacancy.objects.all()

    # Динамика уровня зарплат по годам
    salary_trends = (
        vacancies.values('published_at__year')
        .annotate(avg_salary=Avg(F('salary_from') + F('salary_to')) / 2)
        .order_by('published_at__year')
    )

    # Динамика количества вакансий по годам
    vacancy_trends = (
        vacancies.values('published_at__year')
        .annotate(count=Count('id'))
        .order_by('published_at__year')
    )

    # Уровень зарплат по городам с конвертацией в рубли
    salary_by_area = (
        vacancies.values('area_name')
        .annotate(avg_salary=Avg((F('salary_from') + F('salary_to')) / 2))
        .order_by('-avg_salary')
    )

    # Доля вакансий по городам
    vacancies_by_area = (
        vacancies.values('area_name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # ТОП-20 навыков по годам
    skills_by_year = {}

    for vacancy in vacancies:
        year = vacancy.published_at.year  # Получаем год публикации вакансии
        skills = vacancy.key_skills.split(',')  # Предполагается, что навыки разделены запятыми

        if year not in skills_by_year:
            skills_by_year[year] = []

        skills_by_year[year].extend([skill.strip() for skill in skills])  # Добавляем навыки в список

    top_skills_by_year = {}

    for year, skills in skills_by_year.items():
        skill_counts = Counter(skills)  # Подсчет частоты навыков
        top_skills = skill_counts.most_common(20)  # Получение ТОП-20 навыков
        top_skills_by_year[year] = top_skills

    context = {
        'salary_trends': salary_trends,
        'vacancy_trends': vacancy_trends,
        'salary_by_area': salary_by_area,
        'vacancies_by_area': vacancies_by_area,
        'top_skills_by_year': top_skills_by_year,
    }

    return render(request, 'analytics/statistics.html', context)


def demand(request):
    return render(request, 'analytics/demand.html')


def geography(request):
    return render(request, 'analytics/geography.html')


def skills(request):
    return render(request, 'analytics/skills.html')


def latest_vacancies(request):
    return render(request, 'analytics/latest_vacancies.html')
