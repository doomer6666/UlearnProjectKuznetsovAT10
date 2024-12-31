import aiohttp
import asyncio
import re
from django.shortcuts import render
from .models import SalaryByYear, VacanciesCountByYear, SalaryByCity, VacanciesCountByCity, Skill
from datetime import datetime, timedelta


def get_salary_and_vacancy_data():
    salary_trends = SalaryByYear.objects.all()
    vacancy_trends = VacanciesCountByYear.objects.all()
    return salary_trends, vacancy_trends

def get_skills_data():
    skills_by_year = {}
    images_by_year = {}

    for skill in Skill.objects.all().order_by('year'):
        if skill.year not in skills_by_year:
            skills_by_year[skill.year] = []
        skills_by_year[skill.year].append(skill)

    for year in skills_by_year:
        skills_by_year[year].sort(key=lambda x: x.count, reverse=True)
        images_by_year[year] = f'img/skills_{year}_plot.png'

    return skills_by_year, images_by_year


def index(request):
    return render(request, 'analytics/index.html')


def statistics(request):
    salary_trends, vacancy_trends = get_salary_and_vacancy_data()
    salary_by_city = SalaryByCity.objects.all()
    vacancy_count_by_city = VacanciesCountByCity.objects.all()
    skills_by_year, images_by_year = get_skills_data()

    context = {
        'salary_trends': salary_trends,
        'vacancy_trends': vacancy_trends,
        'salary_by_area': salary_by_city,
        'vacancies_by_area': vacancy_count_by_city,
        'top_skills_by_year': skills_by_year,
        'images_by_year': images_by_year,
    }

    return render(request, 'analytics/statistics.html', context)


def demand(request):
    salary_trends = SalaryByYear.objects.all()
    vacancy_trends = VacanciesCountByYear.objects.all()

    context = {
        'salary_trends': salary_trends,
        'vacancy_trends':vacancy_trends,
    }

    return render(request, 'analytics/demand.html', context)


def geography(request):
    salary_by_city = SalaryByCity.objects.all()
    vacancy_count_by_city = VacanciesCountByCity.objects.all()

    context = {
        'salary_by_area':salary_by_city,
        'vacancies_by_area':vacancy_count_by_city,
    }

    return render(request, 'analytics/geography.html',context)


def skills(request):
    skills_by_year, images_by_year = get_skills_data()

    context = {
        'top_skills_by_year': skills_by_year,
        'images_by_year': images_by_year
    }

    return render(request, 'analytics/skills.html', context)


async def fetch_details(session, url):
    async with session.get(url) as response:
        return await response.json()


def format_date(date_str):
    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    return date_obj.strftime('%d.%m.%Y, %H:%M')


def clean_description(description):
    # Удаляем все <p> HTML теги
    cleanr = re.compile('<p>')
    cleantext = re.sub(cleanr, '', description)
    # Убираем лишние пробелы и стандартизируем текст
    cleantext = re.sub(r'\s+', ' ', cleantext)
    return cleantext.strip()


async def fetch_details(session, url):
    async with session.get(url) as response:
        return await response.json()

def format_date(date_str):
    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    return date_obj.strftime('%d-%m-%Y, %H:%M')

def clean_description(description):
    # Удаляем все <p> теги
    cleanr = re.compile('<p>')
    cleantext = re.sub(cleanr, '', description)
    cleantext = re.sub(r'\s+', ' ', cleantext)
    return cleantext.strip()

def format_salary(salary_from, salary_to, currency):
    if salary_from and salary_to:
        return f"от {salary_from:,} до {salary_to:,} {currency}".replace(",", " ")
    elif salary_from:
        return f"от {salary_from:,} {currency}".replace(",", " ")
    elif salary_to:
        return f"до {salary_to:,} {currency}".replace(",", " ")
    return "Не указано"

async def get_recent_jobs(profession_queries):
    url = 'https://api.hh.ru/vacancies'
    params = {
        'date_from': (datetime.now() - timedelta(days=1)).isoformat(),
        'per_page': 10,
        'order_by': 'publication_time'
    }

    async with aiohttp.ClientSession() as session:
        jobs = []
        tasks = []

        for profession in profession_queries:
            params['text'] = profession
            async with session.get(url, params=params) as response:
                data = await response.json()

            for item in data.get('items', []):
                if any(profession.lower() in item['name'].lower() for profession in profession_queries):
                    tasks.append(fetch_details(session, item['url']))

        details = await asyncio.gather(*tasks)
        for detail_data in details:
            salary_from = detail_data['salary']['from'] if detail_data.get('salary') else None
            salary_to = detail_data['salary']['to'] if detail_data.get('salary') else None
            currency = detail_data['salary']['currency'] if detail_data.get('salary') else 'RUR'
            formatted_salary = format_salary(salary_from, salary_to, currency)

            job = {
                'name': detail_data['name'],
                'company': detail_data['employer']['name'] if detail_data.get('employer') else 'Не указано',
                'salary': formatted_salary,
                'region': detail_data['area']['name'],
                'published_at': format_date(detail_data['published_at']),
                'description': clean_description(detail_data.get('description', 'Нет описания')),
                'skills': ', '.join([skill['name'] for skill in detail_data.get('key_skills', [])])
            }
            jobs.append(job)

    unique_jobs = {(job['name'], job['company']): job for job in jobs}.values()
    return list(unique_jobs)

async def latest_vacancies(request):
    profession_queries = [
        'Системный администратор', 'system admin', 'сисадмин', 'сис админ',
        'системный админ', 'cистемный админ', 'администратор систем', 'системний адміністратор'
    ]

    jobs = await get_recent_jobs(profession_queries)

    return render(request, 'analytics/latest_vacancies.html', {'jobs': jobs[:10]})


