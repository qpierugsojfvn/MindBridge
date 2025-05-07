from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Vacancy, Company, Application
from .forms import CompanyForm, VacancyForm, ApplicationForm

def vacancy_list(request):
    vacancies = Vacancy.objects.filter(is_active=True).order_by('-created_at')

    # Filtering
    employment_type = request.GET.get('employment_type')
    if employment_type:
        vacancies = vacancies.filter(employment_type=employment_type)

    location = request.GET.get('location')
    if location:
        vacancies = vacancies.filter(location_city__icontains=location)

    # Pagination (восстановить!)
    paginator = Paginator(vacancies, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'employment_types': Vacancy.EMPLOYMENT_TYPES,
    }
    return render(request, 'vacancy_list.html', context)

def vacancy_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, is_active=True)
    has_applied = False

    if request.user.is_authenticated:
        has_applied = Application.objects.filter(
            vacancy=vacancy,
            applicant=request.user
        ).exists()

    context = {
        'vacancy': vacancy,
        'has_applied': has_applied,
    }
    return render(request, 'vacancy_detail.html', context)


@login_required
def create_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            messages.success(request, 'Company created successfully!')
            return redirect('careers:my_companies')
    else:
        form = CompanyForm()

    return render(request, 'company_form.html', {'form': form})


@login_required
def my_companies(request):
    companies = Company.objects.filter(created_by=request.user)
    return render(request, 'my_companies.html', {'companies': companies})


@login_required
def create_vacancy(request):
    if request.method == 'POST':
        form = VacancyForm(request.user, request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.created_by = request.user
            vacancy.save()
            messages.success(request, 'Vacancy created successfully!')
            return redirect('careers:vacancy_detail', pk=vacancy.pk)
    else:
        form = VacancyForm(request.user)

    return render(request, 'vacancy_form.html', {'form': form})


@login_required
def apply_vacancy(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, is_active=True)

    if Application.objects.filter(vacancy=vacancy, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this position.')
        return redirect('careers:vacancy_detail', pk=pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.vacancy = vacancy
            application.applicant = request.user
            application.save()
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('careers:vacancy_detail', pk=pk)
    else:
        form = ApplicationForm()

    context = {
        'form': form,
        'vacancy': vacancy,
    }
    return render(request, 'application_form.html', context)


@login_required
def my_applications(request):
    applications = Application.objects.filter(applicant=request.user).order_by('-applied_at')
    return render(request, 'my_applications.html', {'applications': applications})


@login_required
def manage_vacancies(request):
    if not request.user.is_staff:
        vacancies = Vacancy.objects.filter(created_by=request.user)
    else:
        vacancies = Vacancy.objects.all()

    return render(request, 'manage_vacancies.html', {'vacancies': vacancies})


