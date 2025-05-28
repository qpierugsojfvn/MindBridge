from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

admin.site.register(UserProfile)
#
# # Определяем inline-админку для профиля пользователя
# class UserProfileInline(admin.StackedInline):
#     model = UserProfile
#     can_delete = False
#     verbose_name_plural = 'Profile'
#     fk_name = 'user'
#     fields = (
#         'avatar', 'get_avatar_preview',
#         'role', 'phone', 'about', 'bio',
#         'country', 'city', 'portfolio_url'
#     )
#     readonly_fields = ('get_avatar_preview',)
#
#     def get_avatar_preview(self, obj):
#         if obj.avatar:
#             return f'<img src="{obj.avatar.url}" width="150" />'
#         return "No avatar uploaded"
#     get_avatar_preview.short_description = 'Avatar Preview'
#     get_avatar_preview.allow_tags = True
#
# # Кастомизируем стандартную админку пользователя
# class UserAdmin(BaseUserAdmin):
#     inlines = (UserProfileInline,)
#     list_display = (
#         'username', 'email', 'first_name', 'last_name',
#         'is_staff', 'get_role', 'get_phone'
#     )
#     list_select_related = ('profile',)
#     list_filter = ('profile__role', 'is_staff', 'is_superuser', 'is_active')
#     search_fields = ('username', 'first_name', 'last_name', 'email', 'profile__phone')
#
#     def get_role(self, instance):
#         return instance.profile.role
#     get_role.short_description = 'Role'
#
#     def get_phone(self, instance):
#         return instance.profile.phone
#     get_phone.short_description = 'Phone'
#
#     def get_inline_instances(self, request, obj=None):
#         if not obj:
#             return list()
#         return super().get_inline_instances(request, obj)
#
# # Отменяем регистрацию стандартного User и регистрируем наш кастомный
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
#
# # Админка для профилей (отдельно)
# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = (
#         'user', 'role', 'get_avatar_preview',
#         'phone', 'country', 'city'
#     )
#     list_display_links = ('user', 'get_avatar_preview')
#     list_filter = ('role', 'country', 'city')
#     search_fields = ('user__username', 'phone', 'about')
#     readonly_fields = ('get_avatar_preview',)
#     fieldsets = (
#         (None, {
#             'fields': ('user', 'role', 'avatar', 'get_avatar_preview')
#         }),
#         ('Personal Info', {
#             'fields': ('phone', 'about', 'bio'),
#             'classes': ('collapse',)
#         }),
#         ('Location', {
#             'fields': ('country', 'city'),
#             'classes': ('collapse',)
#         }),
#         ('Links', {
#             'fields': ('portfolio_url',),
#             'classes': ('collapse',)
#         }),
#     )
#
#     def get_avatar_preview(self, obj):
#         if obj.avatar:
#             return f'<img src="{obj.avatar.url}" width="150" />'
#         return "No avatar uploaded"
#     get_avatar_preview.short_description = 'Current Avatar'
#     get_avatar_preview.allow_tags = True
#
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('user', 'country', 'city')