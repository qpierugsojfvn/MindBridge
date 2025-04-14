from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from taggit.forms import TagField

from .models import *


class DiscussionForm(ModelForm):
    tags_input = TagField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'comma, separated, tags',
            # 'class': 'form-control'
            # 'placeholder': 'comma, separated, tags',
            'class': 'form-control tags-input',
            'data-url': '/api/tags/',  # URL to fetch existing tags
            'autocomplete': 'off'
        }),
        help_text="Enter tags separated by commas",
        label="Discussion Tags"
    )

    class Meta:
        model = Discussion
        fields = ['title', 'content', 'tags_input']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter discussion title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Enter your discussion content'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # For editing existing discussions
            self.initial['tags_input'] = ", ".join(tag.name for tag in self.instance.tags.all())

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Assign the current user as host
        if self.user:
            instance.host = self.user

        if commit:
            instance.save()
            self.save_m2m()  # Handles taggit's many-to-many relationships

        return instance


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(help_text='Required. Please enter a valid email address.', required=True)

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

        return user
