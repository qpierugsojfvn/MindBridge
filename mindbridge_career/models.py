from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Company(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')

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

    title = models.CharField(max_length=200)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
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
    status_changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('vacancy', 'applicant')

    def __str__(self):
        return f"{self.applicant.username} application for {self.vacancy.title}"