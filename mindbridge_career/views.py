from django.shortcuts import render, get_object_or_404, redirect
from .models import Job, Application
from .forms import ApplicationForm
from django.contrib.auth.decorators import login_required

def job_list(request):
    jobs = Job.objects.select_related('company').order_by('-posted_at')
    return render(request, 'careers/job_list.html', {'jobs': jobs})


def job_detail(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    return render(request, 'careers/job_detail.html', {'job': job})


@login_required
def apply_to_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            return render(request, 'careers/application_success.html', {'job': job})
    else:
        form = ApplicationForm()
    return render(request, 'careers/apply.html', {'form': form, 'job': job})
