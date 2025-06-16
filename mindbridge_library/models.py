from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from embed_video.fields import EmbedVideoField

User = get_user_model()

class Video(models.Model):
    video = EmbedVideoField()

class Lesson(models.Model):
    LESSON_FORMAT_CHOICES = [
        ('video', 'Video'),
        ('article', 'Article'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    format = models.CharField(max_length=10, choices=LESSON_FORMAT_CHOICES)
    content = models.TextField(
        help_text="Main content of the lesson. For videos, this can be a description or transcript.")
    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    duration = models.PositiveIntegerField(blank=True, null=True, help_text="Duration in minutes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons')
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_video_duration(self):
        if self.duration:
            hours = self.duration // 60
            minutes = self.duration % 60
            return f"{hours}h {minutes}m" if hours else f"{minutes}m"
        return None


class LessonAttachment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attachments')
    pdf_file = models.FileField(upload_to='lesson_attachments/')
    title = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.lesson.title}"


class UserLessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progress')
    last_position = models.PositiveIntegerField(default=0,
                                                help_text="Last position in seconds for video or character count for article")
    is_completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username}'s progress on {self.lesson.title}"

    def get_progress_percentage(self):
        if self.lesson.format == 'video' and self.lesson.duration:
            return min(100, int((self.last_position / (self.lesson.duration * 60)) * 100))
        elif self.lesson.format == 'article':
            content_length = len(self.lesson.content)
            if content_length > 0:
                return min(100, int((self.last_position / content_length) * 100))
        return 0
