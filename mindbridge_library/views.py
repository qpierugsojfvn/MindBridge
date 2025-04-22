from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Lesson, LessonAttachment, UserLessonProgress
from .forms import LessonForm, AttachmentForm
from django.db.models import Q, Count


def index(request):
    lesson_list = Lesson.objects.filter(is_published=True).order_by('-created_at')

    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        lesson_list = lesson_list.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # how many lessons per page
    paginator = Paginator(lesson_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Initialize personalized sections
    for_you = None
    continue_section = None

    if request.user.is_authenticated:
        # "For You" recommendations
        completed_lesson_ids = UserLessonProgress.objects.filter(
            user=request.user,
            is_completed=True
        ).values_list('lesson__id', flat=True)

        if completed_lesson_ids.exists():
            # Get lessons with same format as completed ones
            for_you = Lesson.objects.filter(
                is_published=True,
                format__in=Lesson.objects.filter(
                    id__in=completed_lesson_ids
                ).values_list('format', flat=True).distinct()
            ).exclude(
                id__in=completed_lesson_ids
            ).order_by('?')[:6]  # Random sample of 6
        else:
            # Fallback: most popular lessons
            for_you = Lesson.objects.filter(
                is_published=True
            ).annotate(
                popularity=Count('user_progress')
            ).order_by('-popularity')[:6]

        # "Continue Watching/Reading" section
        continue_progress = UserLessonProgress.objects.filter(
            user=request.user,
            is_completed=False
        ).select_related('lesson').order_by('-updated_at')[:4]

        continue_section = [progress.lesson for progress in continue_progress]

    return render(request, 'library_main.html', {
        'page_obj': page_obj,
        'lessons': page_obj.object_list,
        'search_query': search_query,
        'for_you': for_you,
        'continue_section': continue_section,
        'current_filter': request.GET.get('filter')
    })


@login_required
def create_lesson(request):
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.author = request.user
            lesson.save()
            messages.success(request, 'Lesson created successfully!')
            return redirect('lesson_detail', slug=lesson.slug)
    else:
        form = LessonForm()

    return render(request, 'create_lesson.html', {'form': form})


@login_required
def update_lesson(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug, author=request.user)

    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated successfully!')
            return redirect('lesson_detail', slug=lesson.slug)
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'update_lesson.html', {'form': form, 'lesson': lesson})


def lesson_detail(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug)
    attachments = lesson.attachments.all()

    # Get or create user progress
    user_progress = None
    if request.user.is_authenticated:
        user_progress, created = UserLessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'last_position': 0, 'is_completed': False}
        )

    return render(request, 'lesson_detail.html', {
        'lesson': lesson,
        'attachments': attachments,
        'user_progress': user_progress,
    })


@login_required
def add_attachment(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug, author=request.user)

    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.lesson = lesson
            attachment.save()
            messages.success(request, 'Attachment added successfully!')
            return redirect('lesson_detail', slug=lesson.slug)
    else:
        form = AttachmentForm()

    return render(request, 'add_attachment.html', {'form': form, 'lesson': lesson})


@login_required
def update_progress(request, slug):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        lesson = get_object_or_404(Lesson, slug=slug)
        position = int(request.POST.get('position', 0))
        completed = request.POST.get('completed', 'false') == 'true'

        progress, created = UserLessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'last_position': position, 'is_completed': completed}
        )

        if not created:
            progress.last_position = position
            progress.is_completed = completed
            progress.save()

        return JsonResponse({
            'status': 'success',
            'progress': progress.get_progress_percentage()
        })

    return JsonResponse({'status': 'error'}, status=400)


# In views.py
def get_for_you_recommendations(user):
    # Get completed lessons
    completed = UserLessonProgress.objects.filter(
        user=user,
        is_completed=True
    ).values_list('lesson__id', flat=True)

    # Get similar lessons (by tags, format, etc.)
    from django.db.models import Count
    from django.contrib.postgres.aggregates import ArrayAgg

    # Example: Recommend lessons with same format as completed ones
    if completed.exists():
        return Lesson.objects.filter(
            is_published=True,
            format__in=UserLessonProgress.objects.filter(
                user=user,
                lesson__id__in=completed
            ).values_list('lesson__format', flat=True).distinct()
        ).exclude(id__in=completed).annotate(
            similarity_score=Count('format')  # Simple scoring
        ).order_by('-similarity_score', '?')[:6]

    # Fallback: Popular lessons if no history
    return Lesson.objects.filter(
        is_published=True
    ).annotate(
        popularity=Count('userprogress')
    ).order_by('-popularity')[:6]
