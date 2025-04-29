from django.contrib import admin
from embed_video.admin import AdminVideoMixin
from .models import Lesson, LessonAttachment, UserLessonProgress, Video

class LibraryAdmin(AdminVideoMixin, admin.ModelAdmin):
    pass

admin.site.register(Video, LibraryAdmin)

class LessonAttachmentInline(admin.TabularInline):
    model = LessonAttachment
    extra = 1


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'format', 'is_published', 'created_at')
    list_filter = ('format', 'is_published')
    search_fields = ('title', 'description', 'content')
    inlines = [LessonAttachmentInline]


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'get_progress_percentage', 'is_completed')
    list_filter = ('is_completed',)
    search_fields = ('user__username', 'lesson__title')

    def get_progress_percentage(self, obj):
        return f"{obj.get_progress_percentage()}%"

    get_progress_percentage.short_description = 'Progress'
