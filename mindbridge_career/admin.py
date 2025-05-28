from django.contrib import admin
from .models import Company, Vacancy, Application
from mindbridge_auth.models import UserProfile

admin.site.register(Vacancy)
admin.site.register(Application)
admin.site.register(Company)
# admin.site.register(VacancyForm)

#
# @admin.register(Company)
# class CompanyAdmin(admin.ModelAdmin):
#     list_display = ('name', 'website', 'user', 'created_at')
#     search_fields = ('name', 'user__username', 'website')
#     list_filter = ('created_at',)
#     readonly_fields = ('created_at', 'updated_at')
#     fieldsets = (
#         (None, {
#             'fields': ('user', 'name', 'logo', 'description')
#         }),
#         ('Contact Info', {
#             'fields': ('website', 'phone', 'email'),
#             'classes': ('collapse',)
#         }),
#         ('Metadata', {
#             'fields': ('created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
#
#
# @admin.register(Vacancy)
# class VacancyAdmin(admin.ModelAdmin):
#     list_display = ('title', 'company', 'employment_type', 'work_schedule',
#                     'location_city', 'is_active', 'posted_date')
#     list_filter = ('employment_type', 'work_schedule', 'is_active', 'experience_required')
#     search_fields = ('title', 'company__name', 'location_city', 'description')
#     list_editable = ('is_active',)
#     raw_id_fields = ('company',)
#     date_hierarchy = 'posted_date'
#     fieldsets = (
#         (None, {
#             'fields': ('title', 'company', 'description', 'is_active')
#         }),
#         ('Details', {
#             'fields': (
#                 ('employment_type', 'work_schedule'),
#                 ('salary_min', 'salary_max'),
#                 'experience_required'
#             )
#         }),
#         ('Location', {
#             'fields': ('location_city', 'location_country', 'is_remote')
#         }),
#         ('Dates', {
#             'fields': ('posted_date',),
#             'classes': ('collapse',)
#         }),
#     )
#
#
# @admin.register(Application)
# class ApplicationAdmin(admin.ModelAdmin):
#     list_display = ('vacancy', 'applicant', 'status', 'applied_date', 'last_updated')
#     list_filter = ('status', 'vacancy__company', 'vacancy__title')
#     search_fields = ('vacancy__title', 'applicant__username', 'cover_letter')
#     list_editable = ('status',)
#     raw_id_fields = ('vacancy', 'applicant')
#     readonly_fields = ('applied_date', 'last_updated')
#     actions = ['mark_as_reviewed', 'mark_as_rejected']
#
#     def mark_as_reviewed(self, request, queryset):
#         queryset.update(status='REVIEWED')
#
#     mark_as_reviewed.short_description = "Mark selected applications as reviewed"
#
#     def mark_as_rejected(self, request, queryset):
#         queryset.update(status='REJECTED')
#
#     mark_as_rejected.short_description = "Mark selected applications as rejected"
