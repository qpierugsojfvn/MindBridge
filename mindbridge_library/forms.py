from django import forms
from .models import Lesson, LessonAttachment


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

    class Meta:
        model = Lesson
        fields = [
            'title', 'description', 'format',
            'content', 'video_url', 'video_file', 'duration', 'is_published'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'content': forms.Textarea(attrs={'rows': 10}),
        }

    def clean(self):
        cleaned_data = super().clean()
        format = cleaned_data.get('format')
        video_url = cleaned_data.get('video_url')
        video_file = cleaned_data.get('video_file')

        if format == 'video':
            if not video_url and not video_file:
                raise forms.ValidationError("Either video URL or video file is required for video lessons")
            if video_url and video_file:
                raise forms.ValidationError("Please provide either a video URL or upload a video file, not both")

        return cleaned_data

    def save(self, commit=True):
        lesson = super().save(commit=commit)

        # Handle attachment if provided
        if commit and self.cleaned_data.get('attachment'):
            LessonAttachment.objects.create(
                lesson=lesson,
                pdf_file=self.cleaned_data['attachment'],
                title=self.cleaned_data.get('attachment_title', '')
            )

        return lesson


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = LessonAttachment
        fields = ['pdf_file', 'title']
        required=True
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