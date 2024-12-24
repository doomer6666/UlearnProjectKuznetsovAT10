from django.db import models

class Vacancy(models.Model):
    name = models.CharField(max_length=200)
    key_skills = models.TextField()
    salary_from = models.FloatField(null=True, blank=True)
    salary_to = models.FloatField(null=True, blank=True)
    salary_currency = models.CharField(max_length=10)
    area_name = models.CharField(max_length=100)
    published_at = models.DateTimeField()

    def __str__(self):
        return self.name
