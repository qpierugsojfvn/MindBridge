from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone

from MindBridge import settings
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

    # Pagination
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


# careers/views.py
@login_required
def vacancy_applications(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk, created_by=request.user)
    applications = vacancy.applications.all().order_by('-applied_at')

    return render(request, 'vacancy_applications.html', {
        'vacancy': vacancy,
        'applications': applications,
    })


@login_required
def update_application_status(request, pk):
    application = get_object_or_404(Application, pk=pk)
    vacancy = application.vacancy

    # Check if current user owns the vacancy
    if request.user != vacancy.created_by and not request.user.is_staff:
        messages.error(request, "You don't have permission to update this application.")
        return redirect('careers:vacancy_applications', pk=vacancy.pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')

        if new_status in dict(Application.STATUS_CHOICES).keys():
            old_status = application.status
            application.status = new_status
            application.status_changed_at = timezone.now()
            application.notes = notes
            application.save()

            # Send email notification if status changed
            if old_status != new_status:
                subject = f"Your application status has been updated"
                message = f"""Hello {application.applicant.username},

        Your application for {vacancy.title} at {vacancy.company.name} 
        has been updated to: {application.get_status_display()}

        Notes: {notes or 'No additional notes provided'}

        Thank you,
        {vacancy.company.name} Team"""

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [application.applicant.email],
                    fail_silently=True,
                )

            messages.success(request, f"Application status updated to {application.get_status_display()}")

    return redirect('careers:vacancy_applications', pk=vacancy.pk)

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