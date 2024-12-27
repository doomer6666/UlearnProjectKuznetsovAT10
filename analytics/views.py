from django.db.models.functions import Substr, Round
from django.shortcuts import render
from .models import Vacancy, Currency
from django.db.models import Avg, Count, F, Q
from collections import Counter


def index(request):
    return render(request, 'analytics/index.html')


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
    data = Vacancy.objects.all()
    bd = Currency.objects.all()

    vacancy_trends = (
        data.values('published_at__year')
        .annotate(count=Count('id'))
        .order_by('published_at__year')
    )
    # Преобразуем bd в словарь для более удобного доступа
    currency_dict = {(item.date.strftime('%Y-%m-%d'), item.currency_code): item.currency for item in bd}

    # Преобразуем зарплаты в рубли
    for item in data:
        if item.salary_currency and item.salary_currency != 'RUR':
            date = item.published_at.replace(day=1)
            exchange_rate = currency_dict.get((date.strftime('%Y-%m-%d'), item.salary_currency), 0)
            if exchange_rate:
                item.salary_from = float(item.salary_from or 0) * exchange_rate
                item.salary_to = float(item.salary_to or 0) * exchange_rate

    # Фильтруем вакансии, чтобы исключить те, у которых зарплата выше 10 миллионов рублей
    data = data.filter(salary_from__lte=10000000, salary_to__lte=10000000)

    # Рассчитываем среднее значение (salary_from + salary_to) / 2
    data = data.annotate(avg_salary=((F('salary_from') + F('salary_to')) / 2))

    # Исправляем аннотацию года и фильтруем данные, чтобы включить только нужные годы
    data = (data.annotate(year=Substr('published_at', 1, 4))  # Аннотируем данные, извлекая год из даты публикации
            .values('year')  # Группируем данные по годам
            .annotate(avg_salary=Round(Avg('avg_salary'), 2)))  # Рассчитываем среднюю зарплату по годам и округляем до 2 знаков после запятой

    context = {
        'first_parameter': 'avg_salary',
        'second_parameter': 'year',
        'salary_trends': data,
        'vacancy_trends': vacancy_trends,
    }
    return render(request, 'analytics/demand.html',context)



def geography(request):
    return render(request, 'analytics/geography.html')


def skills(request):
    return render(request, 'analytics/skills.html')


def latest_vacancies(request):
    return render(request, 'analytics/latest_vacancies.html')
