from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify

from .models import Lesson, LessonAttachment, CustomTag, UserLessonProgress
from .forms import LessonForm, AttachmentForm
from django.db.models import Q, Count

def index(request, filter_type=None):
    # Determine filter type from URL path
    if request.path.endswith('/articles/'):
        filter_type = 'article'  # Note: using model value 'article' not 'articles'
    elif request.path.endswith('/videos/'):
        filter_type = 'video'  # Note: using model value 'video' not 'videos'

    # Base queryset
    lesson_list = Lesson.objects.filter(is_published=True).order_by('-created_at')

    recent_tags = CustomTag.objects.annotate(
        num_lessons=Count('lesson')
    ).order_by('-num_lessons')[:10]

    tag_filter = request.GET.get('tags')
    if tag_filter:
        lesson_list = lesson_list.filter(tags__name=tag_filter)

    # Apply format filter if specified
    if filter_type in ['article', 'video']:
        lesson_list = lesson_list.filter(format=filter_type)

    #Search lesson
    search_query = request.GET.get('search', '')
    if search_query:
        lesson_list = lesson_list.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(lesson_list, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for_you = None
    continue_section = None

    if request.user.is_authenticated:
        continue_progress = UserLessonProgress.objects.filter(
            user=request.user,
            is_completed=False,
            lesson__is_published=True
        ).select_related('lesson').order_by('-updated_at')[:4]

        continue_section = []
        for progress in continue_progress:
            lesson = progress.lesson
            lesson.progress_percentage = progress.get_progress_percentage()
            continue_section.append(lesson)

        if filter_type in ['article', 'video']:
            continue_section = [lesson for lesson in continue_section
                                if lesson.format == filter_type]

        # continue_section = [progress.lesson for progress in continue_progress[:4]]

        # "For You" recommendations with filter applied
        completed_lesson_ids = UserLessonProgress.objects.filter(
            user=request.user,
            is_completed=True
        ).values_list('lesson__id', flat=True)

        if completed_lesson_ids.exists():
            for_you = Lesson.objects.filter(
                is_published=True,
                format__in=Lesson.objects.filter(
                    id__in=completed_lesson_ids
                ).values_list('format', flat=True).distinct()
            ).exclude(id__in=completed_lesson_ids)

            if filter_type in ['article', 'video']:
                for_you = for_you.filter(format=filter_type)

            for_you = for_you.order_by('?')[:6]
        else:
            for_you = Lesson.objects.filter(
                is_published=True
            )

            if filter_type in ['article', 'video']:
                for_you = for_you.filter(format=filter_type)

            for_you = for_you.annotate(
                popularity=Count('user_progress')
            ).order_by('-popularity')[:6]

    return render(request, 'library_main.html', {
        'page_obj': page_obj,
        'lessons': page_obj.object_list,
        'search_query': search_query,
        'for_you': for_you,
        'continue_section': continue_section,
        'current_filter': filter_type,
        'recent_tags': recent_tags,
    })


@login_required
def create_lesson(request):
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            # First save the lesson without committing to get the ID
            lesson = form.save(commit=False)
            lesson.author = request.user

            # Set slug from title
            lesson.slug = slugify(lesson.title)

            # Ensure slug is unique
            counter = 1
            while Lesson.objects.filter(slug=lesson.slug).exists():
                lesson.slug = f"{slugify(lesson.title)}-{counter}"
                counter += 1

            # Save the lesson to get an ID
            lesson.save()

            # Now save the many-to-many relationships (tags)
            form.save_m2m()

            # Handle attachment if provided
            if 'attachment' in request.FILES:
                LessonAttachment.objects.create(
                    lesson=lesson,
                    pdf_file=request.FILES['attachment'],
                    title=form.cleaned_data.get('attachment_title', 'Attachment')
                )

            messages.success(request, 'Lesson created successfully!')
            return redirect('lesson_detail', slug=lesson.slug)
        else:
            print("Form errors: ", form.errors)
    else:
        print("123")
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

    recent_tags = CustomTag.objects.annotate(
        num_lessons=Count('lesson')
    ).order_by('-num_lessons')[:10]

    # Get related lessons by tags
    related_lessons = Lesson.objects.filter(
        tags__in=lesson.tags.all()
    ).exclude(id=lesson.id).distinct()[:3]

    return render(request, 'lesson_detail.html', {
        'lesson': lesson,
        'attachments': attachments,
        'recent_tags': recent_tags,
        'related_lessons': related_lessons,
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
