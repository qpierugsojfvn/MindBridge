from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    EMPLOYMENT_TYPES = [
        ('FT', 'Full Time'),
        ('PT', 'Part Time'),
        ('PR', 'Project/Task'),
        ('IN', 'Internship'),
    ]

    SCHEDULE_TYPES = [
        ('FD', 'Full Day'),
        ('RE', 'Remote'),
        ('FS', 'Flexible Schedule'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    salary = models.CharField(max_length=100, blank=True)
    employment_type = models.CharField(max_length=2, choices=EMPLOYMENT_TYPES)
    work_schedule = models.CharField(max_length=2, choices=SCHEDULE_TYPES)
    experience_required = models.CharField(max_length=50)
    description = models.TextField()
    location_city = models.CharField(max_length=100)
    location_country = models.CharField(max_length=100)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company.name}"


class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.username} -> {self.job.title}"
