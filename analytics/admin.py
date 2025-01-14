from django.contrib import admin
from .models import Vacancy,Currency,SalaryByYear,VacanciesCountByYear,SalaryByCity,VacanciesCountByCity,Skill


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at')
    search_fields = ('name', 'area_name')
    list_filter = ('salary_currency', 'area_name')

    fieldsets = (
        (None, {
            'fields': ('name', 'key_skills', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at')
        }),
    )

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('date', 'currency_code', 'currency')
    search_fields = ('currency_code',)

@admin.register(SalaryByYear)
class SalaryByYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'avg_salary')
    search_fields = ('year',)

@admin.register(VacanciesCountByYear)
class VacanciesCountByYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'count')
    search_fields = ('year',)

@admin.register(SalaryByCity)
class SalaryByCityAdmin(admin.ModelAdmin):
    list_display = ('area_name', 'avg_salary')
    search_fields = ('area_name',)

@admin.register(VacanciesCountByCity)
class VacanciesCountByCityAdmin(admin.ModelAdmin):
    list_display = ('area_name', 'count')
    search_fields = ('area_name',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('year', 'name', 'count')
    search_fields = ('year', 'name')
