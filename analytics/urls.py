
from django.urls import path
from .views import index, statistics, demand, geography, skills, latest_vacancies

urlpatterns = [
    path('', index, name='home'),
path('demand/', demand, name='demand'),
    path('statistics/', statistics, name='statistics'),
    path('geography/', geography, name='geography'),
    path('skills/', skills, name='skills'),
    path('latest_vacancies/', latest_vacancies, name='latest_vacancies'),
]
