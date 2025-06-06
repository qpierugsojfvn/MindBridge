# Generated by Django 5.2 on 2025-06-01 14:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('COMPANY', 'Company'), ('EMPLOYEE', 'Employee'), ('ADMIN', 'Admin')], max_length=10)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('about', models.TextField(blank=True, max_length=50)),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('avatar', models.ImageField(blank=True, help_text='Upload a profile picture (max 2MB)', null=True, upload_to='avatars/')),
                ('portfolio_url', models.URLField(blank=True, max_length=500, null=True, verbose_name='Portfolio (Behance, Dribbble, etc.)')),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.city')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.country')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
