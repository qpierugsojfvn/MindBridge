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


class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'salary_min', 'salary_max', 'employment_type',
                  'work_schedule', 'experience_required', 'description',
                  'location_city', 'location_country', 'is_remote']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }


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

#
# class VacancyForm(forms.ModelForm):
#     CURRENCY_CHOICES = [
#         ('USD', 'USD ($)'),
#         ('EUR', 'EUR (€)'),
#         ('RUB', 'RUB (₽)'),
#         ('KZT', 'KZT (₸)'),
#     ]
#
#     currency = forms.ChoiceField(
#         choices=CURRENCY_CHOICES,
#         required=False,
#         label='Currency'
#     )
#
#     class Meta:
#         model = Vacancy
#         fields = [
#             'title', 'salary', 'currency', 'employment_type', 'schedule',
#             'experience_required', 'description', 'company',
#             'location_city', 'location_country'
#         ]
#
#     def __init__(self, user, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['company'].queryset = Company.objects.filter(created_by=user)
#
#
# class ApplicationForm(forms.ModelForm):
#     class Meta:
#         model = Application
#         fields = ['cover_letter', 'resume']
#
#     def clean_resume(self):
#         resume = self.cleaned_data.get('resume')
#         if resume:
#             if resume.size > 5 * 1024 * 1024:  # 5MB limit
#                 raise ValidationError("Resume file too large ( > 5MB )")
#             if not resume.name.lower().endswith(('.pdf', '.doc', '.docx')):
#                 raise ValidationError("Only PDF and Word documents are allowed")
#         return resume
#
