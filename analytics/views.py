import requests
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


def load_vacancies(keywords):
    # Формирование запроса к API по ключевым словам
    url = 'https://api.hh.ru/vacancies'
    query = ' OR '.join([f'"{kw}"' for kw in keywords])  # Используем кавычки для целостности ключевых слов
    date_from = (datetime.now() - timedelta(days=1)).isoformat()
    # Параметры запроса к API
    params = {
        'text': query,
        'date_from': date_from,
        'order_by': 'publication_time',
        'per_page': '15',
        'search_field': 'name',  # Ищем ключевые слова только в названии вакансии
    }
    response = requests.get(url, params=params)
    response.raise_for_status()  # Проверка на успешность запроса
    items = response.json().get('items', [])  # Возврат списка вакансий
    print(f"Загружено вакансий: {len(items)}")  # Отладочная информация
    return items


def get_vacancy_info(vacancy_id):
    # Получение информации о конкретной вакансии по ID
    api = f'https://api.hh.ru/vacancies/{vacancy_id}'
    response = requests.get(api)
    response.raise_for_status()  # Проверка на успешность запроса
    return response.json()

def get_salary(salary):
    # Словарь для перевода идентификаторов валют в названия
    currency_map = {
        'RUR': 'рублей',
        'USD': 'долларов',
        'EUR': 'евро',
        'BYN': 'белорусских рублей',
        'KZT': 'тенге',
        'UAH': 'гривен',
        'MDL': 'молдавских леев',
        'AMD': 'драмов',
        'AZN': 'манатов',
        'KGS': 'сомов',
        'TJS': 'сомони',
        'UZS': 'сумов',
        'TMT': 'манатов Туркменистана'
    }

    # Получение и форматирование информации о зарплате
    if not salary:
        return None

    salary_from = salary.get('from')
    salary_to = salary.get('to')
    currency_id = salary.get('currency', '')

    # Перевод идентификатора валюты в название
    currency_name = currency_map.get(currency_id, currency_id)

    # Обработка различных случаев
    if salary_from and salary_to and salary_from != salary_to:
        return f"от {salary_from} до {salary_to} {currency_name}"
    elif salary_from and not salary_to:
        return f"от {salary_from} {currency_name}"
    elif not salary_from and salary_to:
        return f"до {salary_to} {currency_name}"
    elif salary_from == salary_to:
        return f"{salary_from} {currency_name}"
    else:
        return None  # В случае, если все значения отсутствуют или равны None

def latest_vacancies(request):
    # Ключевые слова для поиска вакансий системного администратора
    keywords = ['Системный администратор', 'system administrator', 'сисадмин', 'сис админ', 'системный админ',
                'администратор систем', 'системний адміністратор']

    vacancies = load_vacancies(keywords)
    if not vacancies:
        # Возврат пустого списка, если вакансий не найдено
        return render(request, 'analytics/latest_vacancies.html', {'vacancies': []})

    detailed_vacancies = []
    for vacancy in vacancies:
        # Проверка на наличие ключевых слов в названии вакансии
        if not any(keyword.lower() in vacancy['name'].lower() for keyword in keywords):
            continue

        # Получение детальной информации о каждой вакансии
        details = get_vacancy_info(vacancy['id'])
        salary = details.get('salary', {})
        skills_list = ", ".join(skill['name'] for skill in details.get('key_skills', [])) or 'Не указано'
        # Форматирование даты публикации вакансии
        published_at = datetime.strptime(details.get('published_at'), '%Y-%m-%dT%H:%M:%S%z').strftime('%H:%M %d.%m.%Y')

        detailed_vacancies.append({
            'title': details.get('name'),
            'description': details.get('description'),
            'skills': skills_list,
            'company': details.get('employer', {}).get('name'),
            'salary': get_salary(salary),
            'region': details.get('area', {}).get('name'),
            'published_at': published_at
        })

    # Возврат HTML страницы с вакансиями
    return render(request, 'analytics/latest_vacancies.html', {'vacancies': detailed_vacancies[:10]})
