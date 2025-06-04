# from google.oauth2 import id_token
# from google.auth.transport import requests


from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from taggit.models import Tag

from .forms import *


def home(request):
    if not request.user.is_authenticated:
        return render(request, 'base/welcome_page.html')
    else:
        q = request.GET.get('q', '')
        if q:
            discussions = Discussion.objects.filter(
                Q(tags__name__icontains=q) |
                Q(tags__slug__icontains=q) |
                Q(title__icontains=' ' + q + ' ') |
                Q(content__icontains=' ' + q + ' ')
            ).distinct()
        else:
            discussions = Discussion.objects.all()

        discussions = discussions.annotate(answers_count=Count('answers')).order_by('-updated_at')

        tags = CustomTag.objects.all()[:6]
        discussion_count = discussions.count()
        popular_tags = get_popular_tags()

        if 'recently_viewed' not in request.session:
            request.session['recently_viewed'] = []


        recently_viewed_count = 3
        if len(request.session['recently_viewed']) > recently_viewed_count:
            request.session['recently_viewed'] = request.session['recently_viewed'][:recently_viewed_count]

        recently_viewed_ids = request.session['recently_viewed']
        recently_viewed_discussions = Discussion.objects.filter(id__in=recently_viewed_ids)

        context = {
            'discussions': discussions,
            'tags': tags,
            'discussion_count': discussion_count,
            'popular_tags': popular_tags,
            'recently_viewed_discussions': recently_viewed_discussions
        }
        return render(request, 'base/home.html', context)


def get_three_weeks_activity(request):
    host_id = request.user.id

    today = datetime.now().date()
    current_weekday = today.weekday()  # 0-пн, 6-вс

    # Находим понедельник текущей недели
    current_monday = today - timedelta(days=current_weekday)

    # Вычисляем даты начала периодов
    week3_start = current_monday - timedelta(weeks=2)
    week2_start = current_monday - timedelta(weeks=1)
    week1_start = current_monday

    # Создаем список всех нужных дат
    date_list = []

    # 2 недели назад (полная неделя)
    date_list.extend([week3_start + timedelta(days=x) for x in range(7)])

    # 1 неделя назад (полная неделя)
    date_list.extend([week2_start + timedelta(days=x) for x in range(7)])

    # Текущая неделя (только пройденные дни)
    date_list.extend([week1_start + timedelta(days=x) for x in range(current_weekday + 1)])

    # Получаем даты публикаций хоста за весь период
    published_dates = Discussion.objects.filter(
        host_id=host_id,
        created_at__date__gte=week3_start,
        created_at__date__lte=today
    ).annotate(
        date_only=TruncDate('created_at')
    ).values_list('date_only', flat=True).distinct()

    published_dates = set(published_dates)

    # Формируем результат с датами и флагами
    activity_array = [date in published_dates for date in date_list]

    total_days = len(activity_array)
    active_days = sum(activity_array)
    activity_percent = round((active_days / total_days) * 100) if total_days > 0 else 0

    return {
        'activity_days': activity_array,
        'activity_percent': activity_percent
    }


def discussion(request, pk):
    discussion = Discussion.objects.get(id=pk)
    answers = discussion.answers.all().order_by('-created_at')
    answer_count=answers.count()

    tags = discussion.tags.all()
    popular_tags = get_popular_tags()

    if 'recently_viewed' not in request.session:
        request.session['recently_viewed'] = []

    if pk not in request.session['recently_viewed']:
        request.session['recently_viewed'].insert(0, pk)
        request.session.modified = True

    recently_viewed_count = 3
    if len(request.session['recently_viewed']) > recently_viewed_count:
        request.session['recently_viewed'] = request.session['recently_viewed'][:recently_viewed_count]

    recently_viewed_ids = request.session['recently_viewed']
    recently_viewed_discussions = Discussion.objects.filter(id__in=recently_viewed_ids)

    if request.method == 'POST':
        answer = Answer.objects.create(
            user=request.user,
            discussion=discussion,
            content=request.POST.get('body'),
        )
        if 'tags' in request.POST:
            tag_names = request.POST.getlist('tags')
            discussion.tags.add(*tag_names)

        return redirect('base:discussion', pk=discussion.id)

    top_level_answers = discussion.answers.filter().order_by('created_at')

    context = {'discussion': discussion,
               'answers': answers,
               'answer_count': answer_count,
               'tags': tags,
               'popular_tags': popular_tags,
               'top_level_answers': top_level_answers,
               'recently_viewed_discussions': recently_viewed_discussions,
               }
    return render(request, 'base/discussion.html', context)


def user_profile(request, pk):
    user = get_object_or_404(User, id=pk)

    activity = get_three_weeks_activity(request)
    print(activity.get('activity_days'))
    context = {
        'user': user,
        'profile': user.profile,
        'recent_discussions': Discussion.objects.filter(host=user).order_by('-created_at')[:5],
        'recent_answers': Answer.objects.filter(user=user).order_by('-created_at')[:5],
        'activity_days': activity.get('activity_days'),
        'activity_percent': activity.get('activity_percent')
    }
    return render(request, 'base/profile.html', context)


def edit_profile(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.user != user and not request.user.is_superuser:
        messages.error(request, "You don't have permission to edit this profile.")
        return redirect('user-profile', pk=user.pk)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=user.profile)

        if u_form.is_valid() and p_form.is_valid():
            if 'avatar-clear' in request.POST:
                if user.profile.avatar:
                    user.profile.avatar.delete()
            elif 'avatar' in request.FILES:
                if user.profile.avatar:
                    user.profile.avatar.delete()

            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('base:user-profile', pk=user.pk)
    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user': user
    }
    return render(request, 'base/edit_profile.html', context)


def load_cities(request):
    country_id = request.GET.get('country')
    cities = City.objects.filter(country_id=country_id).order_by('name')
    return JsonResponse(list(cities.values('id', 'name')), safe=False)


def view_discussion(request):
    context = {
        'popular_tags': get_popular_tags(request),
    }
    return render(request, 'base/viewdisscusion.html', context)


# @login_required(login_url='login')
# def create_discussion(request):
#     if request.method == 'POST':
#         new_discussion = Discussion()
#         new_discussion.title = request.POST.get('title')
#         new_discussion.content = request.POST.get('details')
#         new_discussion.host = request.user
#         new_discussion.save()
#
#         tags_list = request.POST.getlist('tags[]')
#         print(tags_list)
#
#         for tag_name in tags_list:
#             tag, create = CustomTag.objects.get_or_create(name=tag_name)
#             print(tag, create)
#             tag.save()
#             new_discussion.tags.add(tag)
#         new_discussion.save()
#
#         return redirect('home')
#     return render(request, 'base/discussion_form.html')

@login_required(login_url='login')
def create_discussion(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        tags_input = request.POST.get('tags', '')

        # Create new discussion
        new_discussion = Discussion.objects.create(
            title=title,
            content=content,
            host=request.user
        )

        # Process tags
        tags_list = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        for tag_name in tags_list:
            tag, created = CustomTag.objects.get_or_create(name=tag_name)
            new_discussion.tags.add(tag)

        messages.success(request, 'Discussion created successfully!')
        return redirect('base:discussion', pk=new_discussion.id)

    # For GET request, render empty form
    return render(request, 'base/discussion_form.html', {
        'is_create': True  # Add this to distinguish between create and update
    })


@login_required(login_url='login')
def update_discussion(request, pk):
    discussion = get_object_or_404(Discussion, id=pk)

    if request.user != discussion.host:
        messages.error(request, 'You don\'t have permission to edit this discussion.')
        return redirect('base:home')

    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        content = request.POST.get('content')
        tags_list = request.POST.get('tags', '').split(',')

        # Update discussion
        discussion.title = title
        discussion.content = content

        # Update tags
        discussion.tags.clear()
        for tag_name in tags_list:
            tag_name = tag_name.strip()
            if tag_name:
                tag, created = CustomTag.objects.get_or_create(name=tag_name)
                discussion.tags.add(tag)

        discussion.save()
        messages.success(request, 'Discussion updated successfully!')
        return redirect('base:discussion', pk=discussion.id)

    # Get current tags as comma-separated string
    current_tags = ', '.join(tag.name for tag in discussion.tags.all())

    context = {
        'discussion': discussion,
        'current_tags': current_tags
    }
    return render(request, 'base/discussion_form.html', context)

# @login_required(login_url='login')
# def update_discussion(request, pk):
    # discussion = Discussion.objects.get(id=pk)
    #
    # if request.user != discussion.host:
    #     messages.error(request, 'You don\'t have permission to edit this discussion.')
    #     return redirect('base:home')
    #
    # if request.method == 'POST':
    #     discussion.title = request.POST.get('title')
    #     discussion.content = request.POST.get('details')
    #
    #     discussion.tags.clear()
    #
    #     tags_list = request.POST.getlist('tags[]')
    #     for tag_name in tags_list:
    #         if tag_name.strip():
    #             tag, created = CustomTag.objects.get_or_create(name=tag_name.strip())
    #             discussion.tags.add(tag)
    #     print(tags_list)
    #     discussion.save()
    #
    #     return redirect('base:home')
    #
    # context = {'discussion': discussion, 'tags': discussion.tags.all()}
    #
    # return render(request, 'base/discussion_form.html', context)


@login_required(login_url='login')
def delete_discussion(request, pk):
    discussion = Discussion.objects.get(id=pk)

    if request.user != discussion.host:
        messages.error(request, 'You don\'t have permission to delete this discussion.')
        return redirect('base:home')

    if request.method == 'POST':
        discussion.delete()
        return redirect('base:home')

    return render(request, 'base/delete.html', {'obj': discussion})


@login_required(login_url='login')
def delete_answer(request, pk):
    answer = Answer.objects.get(id=pk)

    if request.user != answer.user:
        messages.error(request, 'You don\'t have permission to delete this answer.')
        return redirect('base:home')
    if request.method == 'POST':
        answer.delete()
        return redirect('base:home')

    return render(request, 'base/delete.html', {'obj': answer})


def get_popular_tags(days=150, limit=2):
    time_threshold = datetime.now() - timedelta(days=days)

    # Get recent discussions
    recent_discussion_ids = Discussion.objects.filter(
        created_at__gte=time_threshold
    ).values_list('id', flat=True)

    # Get tags for these discussions
    tags = Tag.objects.filter(
        taggit_taggeditem_items__object_id__in=recent_discussion_ids,
        taggit_taggeditem_items__content_type__model='discussion'
    )

    # Count and order
    popular_tags = (
        tags.annotate(tag_count=Count('id'))
        .order_by('-tag_count')
        .values('name', 'slug', 'tag_count')[:limit]
    )

    return popular_tags


class TagAutocompleteView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        tags = Tag.objects.filter(name__icontains=query).values_list('name', flat=True)
        return JsonResponse(list(tags), safe=False)
