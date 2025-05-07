from django.contrib import admin

from .models import Company, Vacancy, Application


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'created_by')
    search_fields = ('name', 'created_by__username')
    list_filter = ('created_by',)

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'employment_type', 'location_city', 'is_active')
    list_filter = ('employment_type', 'schedule', 'is_active')
    search_fields = ('title', 'company__name', 'location_city')
    raw_id_fields = ('company', 'created_by')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('vacancy', 'applicant', 'status', 'applied_at')
    list_filter = ('status', 'vacancy__company')
    search_fields = ('vacancy__title', 'applicant__username')
    raw_id_fields = ('vacancy', 'applicant')