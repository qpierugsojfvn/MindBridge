from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from mindbridge_auth.models import UserProfile, Interest
from .models import *
import re


def validate_phone_number(value):
    pattern = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
    if not re.match(pattern, value):
        raise ValidationError('Введите корректный номер телефона')


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        help_text='Required. Please enter a valid email address.',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    company_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company Name'
        })
    )
    phone = forms.CharField(
        required=False,
        validators=[validate_phone_number],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+7 (XXX) XXX-XX-XX'
        })
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    username = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'company_name', 'email', 'username', 'password1']

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
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    bio = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'E.g. Graphic Designer specializing in branding'
        })
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'E.g. New York, USA'
        })
    )
    about = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': "Tell others about yourself...",
            'rows': 5
        })
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/*'
        })
    )
    interests = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        help_text="Comma-separated list of interests"
    )
    cover_photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = UserProfile
        fields = ['avatar', 'cover_photo', 'bio', 'location', 'about', 'interests']

    def clean_profile_pic(self):
        picture = self.cleaned_data.get('avatar')
        if picture and picture.size > 2 * 1024 * 1024:  # 2MB limit
            raise ValidationError("Image file too large ( > 2MB )")
        return picture

    def clean_cover_photo(self):
        cover_photo = self.cleaned_data.get('cover_photo')
        if cover_photo:
            try:
                # This ensures the file is readable
                cover_photo.open()
                cover_photo.seek(0)
            except Exception as e:
                raise forms.ValidationError("Couldn't read the uploaded file. Please try again.")
        return cover_photo

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Set initial value for interests as comma-separated string
            self.initial['interests'] = ','.join(
                self.instance.interests.values_list('name', flat=True)
            )

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()

        # Handle interests
        if 'interests' in self.cleaned_data:
            interests = [i.strip() for i in self.cleaned_data['interests'].split(',') if i.strip()]
            profile.interests.clear()
            for interest_name in interests:
                interest, created = Interest.objects.get_or_create(name=interest_name)
                profile.interests.add(interest)

        return profile
