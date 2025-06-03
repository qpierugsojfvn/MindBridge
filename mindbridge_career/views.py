# careers/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Vacancy, Application, Company
from .forms import VacancyForm, ApplicationForm, UserProfileForm
from mindbridge_auth.decorators import role_required
from mindbridge_auth.models import UserProfile
from django.core.exceptions import ObjectDoesNotExist

# careers/views.py
def vacancy_list(request):
    vacancies = Vacancy.objects.filter(is_active=True)

    # Filter by search query
    query = request.GET.get('q')
    if query:
        vacancies = vacancies.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(company__name__icontains=query)
        )

    # Filter by other parameters
    employment_type = request.GET.get('employment_type')
    if employment_type:
        vacancies = vacancies.filter(employment_type=employment_type)

    # Add more filters as needed

    return render(request, 'careers/vacancy_list.html', {'vacancies': vacancies})

def vacancy_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, is_active=True)
    return render(request, 'careers/vacancy_detail.html', {'vacancy': vacancy})

@login_required
@role_required(['COMPANY', 'ADMIN'])
def post_vacancy(request):
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.company = request.user.company_profile
            vacancy.save()
            return redirect('vacancy_detail', pk=vacancy.pk)
    else:
        form = VacancyForm()
    return render(request, 'careers/post_vacancy.html', {'form': form})

@login_required
@role_required(['EMPLOYEE', 'ADMIN'])
def apply_vacancy(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, is_active=True)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.vacancy = vacancy
            application.applicant = request.user
            application.save()
            return redirect('application_status', pk=application.pk)
    else:
        form = ApplicationForm()
    return render(request, 'careers/apply_vacancy.html', {'form': form, 'vacancy': vacancy})

@login_required
def application_status(request, pk):
    application = get_object_or_404(Application, pk=pk, applicant=request.user)
    return render(request, 'careers/application_status.html', {'application': application})

@login_required
@role_required(['COMPANY', 'ADMIN'])
def company_dashboard(request):
    try:
        company = Company.objects.get(user=request.user)
    except Company.DoesNotExist:
        company = None

    if company:
        vacancies = Vacancy.objects.filter(company=company)
        applications = Application.objects.filter(vacancy__in=vacancies)
    else:
        vacancies = Vacancy.objects.none()
        applications = Application.objects.none()

    return render(request, 'careers/company_dashboard.html', {
        'company': company,
        'vacancies': vacancies,
        'applications': applications
    })


@login_required
def complete_profile(request):
    # try:
    #     # profile = request.user.userprofile
    #     return redirect('base:home')  # Profile already exists
    # except ObjectDoesNotExist:
    #     pass

    if request.method == 'POST':
        user = request.user
        form = UserProfileForm(request.POST)
        if form.is_valid():
            # Получаем или создаем профиль пользователя
            profile, created = UserProfile.objects.get_or_create(user=user)
            # Обновляем поля профиля из формы
            profile.role = form.cleaned_data['role']
            profile.phone = form.cleaned_data['phone']
            profile.save()

            # Обновляем поля пользователя
            user.role = profile.role
            user.phone = profile.phone
            user.save()

            return redirect('base:home')
    else:
        form = UserProfileForm()
    return render(request, 'careers/complete_profile.html', {'form': form})


@login_required
@role_required(['COMPANY', 'ADMIN'])
def toggle_vacancy(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, company=request.user.company_profile)
    vacancy.is_active = not vacancy.is_active
    vacancy.save()
    return redirect('careers:company_dashboard')

@login_required
@role_required(['COMPANY', 'ADMIN'])
def update_application_status(request, pk):
    application = get_object_or_404(Application, pk=pk, vacancy__company=request.user.company_profile)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES).keys():
            application.status = new_status
            application.save()
    return redirect('careers:company_dashboard')

@login_required
@role_required(['COMPANY', 'ADMIN'])
def application_detail(request, pk):
    application = get_object_or_404(
        Application.objects.select_related('applicant', 'vacancy'),
        pk=pk,
        vacancy__company=request.user.company_profile
    )
    return render(request, 'careers/application_detail.html', {'application': application})