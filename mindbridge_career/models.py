# careers/models.py
from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    description = models.TextField()
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    EMPLOYMENT_TYPES = [
        ('FULL', 'Full Time'),
        ('PART', 'Part Time'),
        ('PROJ', 'Project/Task'),
        ('INTERN', 'Internship'),
    ]

    WORK_SCHEDULES = [
        ('FULL', 'Full Day'),
        ('REMOTE', 'Remote'),
        ('FLEX', 'Flexible Schedule'),
    ]

    EXPERIENCE_LEVELS = [
        ('NONE', 'No experience'),
        ('1YR', '1 year'),
        ('2YR', '2 years'),
        ('3YR', '3 years'),
        ('5YR', '5+ years'),
    ]

    title = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    employment_type = models.CharField(max_length=10, choices=EMPLOYMENT_TYPES)
    work_schedule = models.CharField(max_length=10, choices=WORK_SCHEDULES)
    experience_required = models.CharField(max_length=10, choices=EXPERIENCE_LEVELS)
    description = models.TextField()
    location_city = models.CharField(max_length=100)
    location_country = models.CharField(max_length=100)
    is_remote = models.BooleanField(default=False)
    posted_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.company.name}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('APPLIED', 'Applied'),
        ('REVIEWED', 'Reviewed'),
        ('INTERVIEW', 'Interview'),
        ('OFFER', 'Offer'),
        ('HIRED', 'Hired'),
        ('REJECTED', 'Rejected'),
    ]

    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    application_date = models.DateTimeField(auto_now_add=True)
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='APPLIED')

    def __str__(self):
        return f"{self.applicant.username}'s application for {self.vacancy.title}"