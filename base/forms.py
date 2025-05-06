from dataclasses import fields

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from taggit.forms import TagField

from .models import *


class DiscussionForm(ModelForm):
    tags = TagField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'comma, separated, tags',
            'class': 'form-control tags-input',
            'data-url': '/api/tags/',
            'autocomplete': 'off'
        }),
        help_text="Enter tags separated by commas",
        label="Discussion Tags"
    )

    class Meta:
        model = Discussion
        fields = ['title', 'content', 'tags']
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
        if self.instance.pk:
            self.initial['tags'] = ", ".join(tag.name for tag in self.instance.tags.all())

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.user:
            instance.host = self.user

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(help_text='Required. Please enter a valid email address.', required=True)

    class Meta:
        model = get_user_model()
        # fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        fields = ['first_name', 'last_name', 'email', 'username', 'password1']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password2']
        self.fields['password1'].help_text = "Enter your password"

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()

        return user

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class ProfileUpdateForm(forms.ModelForm):
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/*'
        }),
        help_text="Upload a profile picture (max 2MB)"
    )

    class Meta:
        model = UserProfile
        fields = ['avatar', 'about', 'description', 'country', 'city', 'portfolio_url']
        widgets = {
            'about': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'country': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-control'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].queryset = City.objects.none()

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['city'].queryset = City.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.country:
            self.fields['city'].queryset = self.instance.country.city_set.order_by('name')

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2 * 1024 * 1024:  # 2MB limit
                raise ValidationError("Image file too large ( > 2MB )")
            return avatar
        return None

    # class Meta:
    #     model = UserProfile
    #     # fields = ['bio', 'profile_pic']
    #     fields = ['about', 'description', 'portfolio_url']
    #
    # def clean_profile_pic(self):
    #     picture = self.cleaned_data.get('profile_pic')
    #     if picture:
    #         if picture.size > 2 * 1024 * 1024:  # 2MB limit
    #             raise ValidationError("Image file too large ( > 2MB )")
    #         return picture
    #     return None