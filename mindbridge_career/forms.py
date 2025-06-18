from django import forms
from .models import Vacancy, Company, Application
from mindbridge_auth.models import UserProfile
from django.core.exceptions import ValidationError


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'description', 'website', 'logo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['logo'].required = False

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 5}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'phone']


class VacancyForm(forms.ModelForm):
    CURRENCY_CHOICES = [
        ('USD', 'USD ($)'),
        ('EUR', 'EUR (€)'),
        ('RUB', 'RUB (₽)'),
        ('KZT', 'KZT (₸)'),
    ]
    EMPLOYMENT_TYPES = [
        ('FULL', 'Full Time'),
        ('PART', 'Part Time'),
        ('PROJ', 'Project/Task'),
        ('INTERN', 'Internship'),
    ]
    WORK_SCHEDULES = [
        ('FULL', 'Full Day'),
        ('REMOTE', 'Remote'),
        ('FLEX', 'Flexible Schedule'),
    ]

    currency = forms.ChoiceField(
        choices=CURRENCY_CHOICES,
        required=False,
        label='Currency'
    )

    salary = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )

    title = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Vacancy title'
        })
    )

    employment_type = forms.ChoiceField(
        choices=EMPLOYMENT_TYPES,
        required=True
    )
    work_schedule = forms.ChoiceField(
        choices=WORK_SCHEDULES,
        required=False
    )
    description = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Vacancy description'
        })
    )
    location_city = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Location city'
        })
    )
    EXPERIENCE_LEVELS = [
        ('NONE', 'No experience'),
        ('1YR', '1 year'),
        ('2YR', '2 years'),
        ('3YR', '3 years'),
        ('5YR', '5+ years'),
    ]
    experience_required = forms.ChoiceField(
        choices=EXPERIENCE_LEVELS,
        required=False
    )

    class Meta:
        model = Vacancy
        fields = [
            'title', 'salary', 'currency', 'employment_type',
            'work_schedule', 'experience_required', 'description',
            'location_city', 'location_country'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Упрощаем выбор для некоторых полей
        self.fields['employment_type'].widget = forms.Select(choices=Vacancy.EMPLOYMENT_TYPES)
        self.fields['work_schedule'].widget = forms.Select(choices=Vacancy.WORK_SCHEDULES)
        self.fields['experience_required'].widget = forms.Select(choices=Vacancy.EXPERIENCE_LEVELS)

