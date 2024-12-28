from django.db import models

class Vacancy(models.Model):
    name = models.CharField(max_length=200)
    key_skills = models.TextField()
    salary_from = models.FloatField(null=True, blank=True)
    salary_to = models.FloatField(null=True, blank=True)
    salary_currency = models.CharField(max_length=10)
    area_name = models.CharField(max_length=100)
    published_at = models.DateTimeField()

    class Meta:
        verbose_name_plural = "Vacancies"

    def __str__(self):
        return self.name


class Currency(models.Model):
    date = models.DateField(max_length=8)
    currency_code = models.CharField(max_length=3)
    currency = models.FloatField()

    class Meta:
        unique_together = ('date', 'currency_code')
        verbose_name_plural = 'Currency Rates'
        db_table = 'currencies'


class SalaryByYear(models.Model):
    year = models.CharField(max_length=4)
    avg_salary = models.FloatField()

    class Meta:
        verbose_name_plural = "Currency Statistics"
        db_table = 'currency_statistics'


class VacanciesCountByYear(models.Model):
    year = models.CharField(max_length=4)
    count = models.IntegerField()

    class Meta:
        verbose_name_plural = "Vacancy Count Statistics"
        db_table = 'vacancies_count_by_year'


class SalaryByCity(models.Model):
    area_name = models.CharField(max_length=100)
    avg_salary = models.FloatField()

    class Meta:
        verbose_name_plural = "SalaryByCity Statistics"
        db_table = 'salary_by_city_statistics'