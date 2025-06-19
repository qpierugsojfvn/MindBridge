from django import forms
from .models import Lesson, LessonAttachment, CustomTag


class LessonForm(forms.ModelForm):
    attachment = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': '.pdf',
            'class': 'file-upload-input'
        }),
        help_text="Upload a PDF attachment (optional, max 5MB)"
    )
    attachment_title = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Attachment title'
        })
    )
    tag_names = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Comma-separated tags (e.g., python, django, web-development)'
        }),
        help_text="Enter tags separated by commas"
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10}),
        required=False,  # Теперь поле необязательное
    )

    class Meta:
        model = Lesson
        fields = [
            'title', 'description', 'format',
            'content', 'video_url', 'video_file', 'duration', 'is_published'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'rows': 10}),
            'format': forms.Select(attrs={'onchange': "toggleFields()"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['duration'].widget.attrs['readonly'] = True
        if self.instance.pk:
            self.fields['tag_names'].initial = ', '.join(tag.name for tag in self.instance.tags.all())

    def clean(self):
        cleaned_data = super().clean()
        format = cleaned_data.get('format')
        content = cleaned_data.get('content')
        video_url = cleaned_data.get('video_url')
        video_file = cleaned_data.get('video_file')
        attachment = cleaned_data.get('attachment')

        if format == 'video':
            if not video_url and not video_file:
                raise forms.ValidationError("Either video URL or video file is required for video lessons")
            if video_url and video_file:
                raise forms.ValidationError("Please provide either a video URL or upload a video file, not both")
            if attachment:
                raise forms.ValidationError("Attachments are not allowed for video lessons")
            if content:
                raise forms.ValidationError("Content field should be empty for video lessons")
        else:  # article
            if not content:
                raise forms.ValidationError("Content is required for articles")
            if video_url or video_file:
                raise forms.ValidationError("Video fields should be empty for articles")

        return cleaned_data

    def save(self, commit=True):
        lesson = super().save(commit=False)

        if commit:
            # Save the lesson first to get an ID
            lesson.save()

            # Save many-to-many relationships
            self.save_m2m()

            # Handle tags
            tag_names = self.cleaned_data.get('tag_names', '')
            if tag_names:
                lesson.tags.clear()  # Clear existing tags if editing
                for name in [name.strip() for name in tag_names.split(',') if name.strip()]:
                    tag, created = CustomTag.objects.get_or_create(name=name.lower())
                    lesson.tags.add(tag)

        return lesson


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = LessonAttachment
        fields = ['pdf_file', 'title']
        required = True
        widgets = {
            'pdf_file': forms.FileInput(attrs={
                'accept': '.pdf',
                'class': 'file-upload-input'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter a title for this attachment'
            })
        }

    def clean_pdf_file(self):
        pdf_file = self.cleaned_data.get('pdf_file')
        if pdf_file:
            # Validate file type
            if not pdf_file.name.endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed")

            # Validate file size (5MB max)
            if pdf_file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File too large (max 5MB)")

        return pdf_file
