from django.contrib import admin
from .models import Vacancy


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
