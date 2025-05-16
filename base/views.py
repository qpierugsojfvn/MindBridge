# from google.oauth2 import id_token
# from google.auth.transport import requests


from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from taggit.models import Tag

from .forms import *



# @user_not_authenticated
# def signup_page(request):
#     page = 'signup'
#     form = UserRegistrationForm(request.POST or None)
#
#     if request.method == 'POST':
#         if form.is_valid():
#             email = form.cleaned_data.get('email')
#
#             if User.objects.filter(email=email).exists():
#                 messages.error(request, 'This email is already registered. Please use a different email.')
#                 return render(request, 'base/login_signup.html', {'page': page, 'form': form})
#
#             user = form.save(commit=False)
#             user.username = user.username.lower()
#             user.is_active = False
#             user.save()
#
#             activateEmail(request, user, email)
#
#             return render(request, 'base/login_signup.html', {'page': page})
#
#         else:
#             messages.error(request, 'Please correct the errors below.')
#
#     context = {'page': page, 'form': form}
#     return render(request, 'base/login_signup.html', context)


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

        tags = Tag.objects.all()[:6]
        discussion_count = discussions.count()

        context = {'discussions': discussions, 'tags': tags, 'discussion_count': discussion_count}
        return render(request, 'base/home.html', context)


def discussion(request, pk):
    discussion = Discussion.objects.get(id=pk)
    answers = discussion.answers.all().order_by('-created_at')

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

        return redirect('discussion', pk=discussion.id)

    top_level_answers = discussion.answers.filter().order_by('created_at')

    context = {'discussion': discussion,
               'answers': answers,
               'tags': tags,
               'popular_tags': popular_tags,
               'top_level_answers': top_level_answers,
               'recently_viewed_discussions': recently_viewed_discussions,
               }
    return render(request, 'base/discussion.html', context)


def user_profile(request, pk):
    user = get_object_or_404(User, id=pk)
    context = {
        'user': user,
        'profile': user.profile,
        'recent_discussions': Discussion.objects.filter(host=user).order_by('-created_at')[:5],
        'recent_answers': Answer.objects.filter(user=user).order_by('-created_at')[:5]
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
            return redirect('user-profile', pk=user.pk)
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
    return render(request, 'base/viewdisscusion.html')

@login_required(login_url='login')
def create_discussion(request):
    if request.method == 'POST':
        new_discussion = Discussion()
        new_discussion.title = request.POST.get('title')
        new_discussion.content = request.POST.get('details')
        new_discussion.host = request.user
        new_discussion.save()

        tags_list = request.POST.getlist('tags[]')
        print(tags_list)

        for tag_name in tags_list:
            tag, create = CustomTag.objects.get_or_create(name=tag_name)
            print(tag, create)
            tag.save()
            new_discussion.tags.add(tag)
        new_discussion.save()

        return redirect('home')
    return render(request, 'base/discussion_form.html')


@login_required(login_url='login')
def update_discussion(request, pk):
    discussion = Discussion.objects.get(id=pk)

    if request.user != discussion.host:
        messages.error(request, 'You don\'t have permission to edit this discussion.')
        return redirect('home')

    if request.method == 'POST':
        discussion.title = request.POST.get('title')
        discussion.content = request.POST.get('details')

        # Очищаем все текущие теги
        discussion.tags.clear()

        # Добавляем новые теги
        tags_list = request.POST.getlist('tags[]')
        for tag_name in tags_list:
            if tag_name.strip():  # Проверяем, что тег не пустой
                tag, created = CustomTag.objects.get_or_create(name=tag_name.strip())
                discussion.tags.add(tag)
        print(tags_list)
        discussion.save()

        return redirect('home')

    context = {'discussion': discussion, 'tags': discussion.tags.all()}

    return render(request, 'base/discussion_form.html', context)


@login_required(login_url='login')
def delete_discussion(request, pk):
    discussion = Discussion.objects.get(id=pk)

    if request.user != discussion.host:
        messages.error(request, 'You don\'t have permission to delete this discussion.')
        return redirect('home')

    if request.method == 'POST':
        discussion.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': discussion})


@login_required(login_url='login')
def delete_answer(request, pk):
    answer = Answer.objects.get(id=pk)

    if request.user != answer.user:
        messages.error(request, 'You don\'t have permission to delete this answer.')
        return redirect('home')
    if request.method == 'POST':
        answer.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': answer})


def get_popular_tags(days=50, limit=3):
    time_threshold = datetime.now() - timedelta(days=days)

    popular_tags = (
        TaggedItem.objects.filter(
            content_type__model='discussion',
            object_id__in=Discussion.objects.filter(
                created_at__gte=time_threshold
            ).values('id')
        )
        .values('tag__name', 'tag__slug')
        .annotate(tag_count=Count('tag'))
        .order_by('-tag_count')  # Descending order
    )

    return popular_tags[:limit]


class TagAutocompleteView(View):
    def get(self, request):
        query = request.GET.get('q', '')
        tags = Tag.objects.filter(name__icontains=query).values_list('name', flat=True)
        return JsonResponse(list(tags), safe=False)
