from django import forms
from .models import Lesson, LessonAttachment


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            'title', 'description', 'format',
            'content', 'video_url', 'duration', 'is_published'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'rows': 10}),
        }

    def clean(self):
        cleaned_data = super().clean()
        format = cleaned_data.get('format')
        video_url = cleaned_data.get('video_url')

        if format == 'video' and not video_url:
            self.add_error('video_url', 'Video URL is required for video lessons')

        return cleaned_data


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = LessonAttachment
        fields = ['pdf_file', 'title']
