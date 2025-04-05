from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import *


class DiscussionForm(ModelForm):
    # class Meta:
    #     model = Discussion
    #     fields = '__all__'
    #     exclude = ['host', 'participants']

    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'comma, separated, tags'
        }),
        help_text="Enter tags separated by commas"
    )

    class Meta:
        model = Discussion
        fields = ['title', 'content', 'tags_input']  # Exclude the actual tags field

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            tags = self.instance.tags.all()
            self.initial['tags_input'] = ", ".join(tag.name for tag in tags)

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

        # Clear existing tags
        instance.tags.clear()

        # Add new tags
        tags_str = self.cleaned_data.get('tags_input', '')
        if tags_str:
            tag_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            instance.tags.add(*tag_list)

        self.save_m2m()  # Important for many-to-many relationships
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
