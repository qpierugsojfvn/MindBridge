import os

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
# from google.oauth2 import id_token
# from google.auth.transport import requests


from datetime import datetime, timedelta
# from imaplib import Flags

from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from taggit.models import Tag
from django.core.mail import EmailMessage

from .forms import *
from .decorators import user_not_authenticated
from .tokens import account_activation_token
from .utils import custom_slugify_


def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User doesn\'t exist.')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    context = {'page': page}
    return render(request, 'base/login_signup.html', context)


def logout_page(request):
    logout(request)
    return redirect('home')


def success(request):
    return redirect('home')


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('home')


# def activateEmail(request, user, to_email):
#     User = get_user_model()
#
#     if User.objects.filter(email=to_email).exclude(pk=user.pk).exists():
#         messages.error(request, f'Email {to_email} is already in use by another account.')
#         return False
#     else:
#         mail_subject = "Activate your user account."
#         message = render_to_string("base/template_activate_account.html", {
#             'user': user.username,
#             'domain': get_current_site(request).domain,
#             'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#             'token': account_activation_token.make_token(user),
#             "protocol": 'https' if request.is_secure() else 'http'
#         })
#         email = EmailMessage(mail_subject, message, to=[to_email])
#         if email.send():
#             messages.success(request, f'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
#                         received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
#         else:
#             messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')
#
# # @csrf_exempt
# # def auth_receiver(request):
# #     """
# #     Google calls this URL after the user has signed in with their Google account.
# #     """
# #     print('Inside')
# #     token = request.POST['credential']
# #
# #     try:
# #         user_data = id_token.verify_oauth2_token(
# #             token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
# #         )
# #     except ValueError:
# #         return HttpResponse(status=403)
# #
# #     # In a real app, I'd also save any new user here to the database.
# #     # You could also authenticate the user here using the details from Google (https://docs.djangoproject.com/en/4.2/topics/auth/default/#how-to-log-a-user-in)
# #     request.session['user_data'] = user_data
# #
# #     return redirect('sign_in')


def activateEmail(request, user, to_email):
    User = get_user_model()

    if User.objects.filter(email=to_email).exclude(pk=user.pk).exists():
        messages.error(request, f'Email {to_email} is already in use by another account.')
        return False

    mail_subject = "Activate your user account."
    message = render_to_string("base/template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])

    try:
        if email.send():
            messages.success(request,
                             f'Dear <b>{user}</b>, please go to your email <b>{to_email}</b> inbox and click on the received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
            return True
        else:
            messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')
            return False
    except Exception as e:
        messages.error(request, f'Error sending email: {str(e)}')
        return False


@user_not_authenticated
def signup_page(request):
    page = 'signup'
    form = UserRegistrationForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data.get('email')

            if User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered. Please use a different email.')
                return render(request, 'base/login_signup.html', {'page': page, 'form': form})

            user = form.save(commit=False)
            user.username = user.username.lower()
            user.is_active = False
            user.save()

            if not activateEmail(request, user, email):
                return render(request, 'base/login_signup.html', {'page': page, 'form': form})

            return redirect('login')  # Redirect to login after successful signup

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    context = {'page': page, 'form': form}
    return render(request, 'base/login_signup.html', context)


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
    tagged_items = GenericRelation(TaggedItem, related_query_name='discussion')
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
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)
            discussion.host = request.user
            discussion.save()

            tags_list = form.cleaned_data.get('tags_input', '')

            for tag_name in tags_list:
                tag, created = Tag.objects.get_or_create(
                    name=tag_name,
                    defaults={'slug': custom_slugify_(tag_name)},
                )
                discussion.tags.add(*tags_list)

            return redirect('home')
    else:
        form = DiscussionForm()

    return render(request, 'base/discussion_form.html', {'form': form})


@login_required(login_url='login')
def update_discussion(request, pk):
    discussion = Discussion.objects.get(id=pk)

    if request.user != discussion.host:
        messages.error(request, 'You don\'t have permission to edit this discussion.')
        return redirect('home')

    if request.method == 'POST':
        form = DiscussionForm(request.POST, instance=discussion, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = DiscussionForm(instance=discussion, user=request.user)

    context = {'form': form}
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
