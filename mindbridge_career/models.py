from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Company(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')

    class Meta:
        app_label = 'mindbridge_career'  # Критически важная строка
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    EMPLOYMENT_TYPES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('project', 'Project/Task'),
        ('internship', 'Internship'),
    ]

    SCHEDULE_TYPES = [
        ('full_day', 'Full Day'),
        ('remote', 'Remote'),
        ('flexible', 'Flexible Schedule'),
    ]

    EXPERIENCE_LEVELS = [
        ('no_exp', 'No experience'),
        ('1_year', '1 year'),
        ('2_years', '2 years'),
        ('3_years', '3 years'),
        ('5_years', '5 years'),
        ('5_plus', '5+ years'),
    ]

    CURRENCY_CHOICES = [
        ('USD', 'USD ($)'),
        ('EUR', 'EUR (€)'),
        ('RUB', 'RUB (₽)'),
        ('KZT', 'KZT (₸)'),
    ]

    title = models.CharField(max_length=200)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD'
    )
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES)
    schedule = models.CharField(max_length=20, choices=SCHEDULE_TYPES)
    experience_required = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS)
    description = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vacancies')
    location_city = models.CharField(max_length=100)
    location_country = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacancies')

    def currency_symbol(self):
        symbols = {
            'USD': '$',
            'EUR': '€',
            'RUB': '₽',
            'KZT': '₸',
        }
        return symbols.get(self.currency, self.currency)

    class Meta:
        app_label = 'mindbridge_career'
        verbose_name = 'Vacancy'
        verbose_name_plural = 'Vacancies'

    def __str__(self):
        return f"{self.title} at {self.company.name}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('interview', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]

    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'mindbridge_career'  # Критически важная строка
        unique_together = ('vacancy', 'applicant')
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'

    def __str__(self):
        return f"{self.applicant.username} application for {self.vacancy.title}"
