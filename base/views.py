from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation.trans_null import activate
from taggit.managers import TaggableManager
from taggit.models import Tag, TaggedItem
from django.core.mail import EmailMessage

from .models import Discussion, Answer
from .forms import DiscussionForm, UserRegistrationForm
from .decorators import user_not_authenticated
from .tokens import account_activation_token

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

    return redirect('homepage')

def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("base/template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
                    received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')


@user_not_authenticated
def signup_page(request):
    page = 'signup'
    form = UserRegistrationForm(request.POST or None)
    if request.method == 'POST':
        # form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.is_active = False
            user.save()

            activateEmail(request, user, form.cleaned_data.get('email'))

            return redirect('home')
        else:
            messages.error(request, 'An unexpected error occurred.')

    context = {'page': page, 'form': form}
    return render(request, 'base/login_signup.html', context)


def home(request):
    q = request.GET.get('q', '')
    if q:
        discussions = Discussion.objects.filter(
            Q(tags__name__icontains=q) |
            Q(tags__slug__icontains=q) |
            Q(title__icontains=q) |
            Q(content__icontains=q)
        ).distinct()
    else:
        discussions = Discussion.objects.all()

    discussions = discussions.annotate(answers_count=Count('answers')).order_by('-updated_at').order_by()

    tags = Tag.objects.all()
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
        if 'tags' in request.POST:  # Check if tags are being submitted
            tag_names = request.POST.getlist('tags')  # Get a list of tag names from the form
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
    user = User.objects.get(id=pk)
    print(user, pk)
    context = {'user': user}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def create_discussion(request):
    if request.method == 'POST':
        form = DiscussionForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            return redirect('home')
    else:
        form = DiscussionForm()

    return render(request, 'base/discussion_form.html', {'form': form})
    # form = DiscussionForm()
    # if request.method == 'POST':
    #     Discussion.objects.create(
    #         host=request.user,
    #         tags=request.POST.getlist('tags'),
    #         title=request.POST.get('title'),
    #         content=request.POST.get('content'),
    #     )
    #     return redirect('home')
    # context = {'form': form}
    # return render(request, 'base/discussion_form.html', context)


@login_required(login_url='login')
def update_discussion(request, pk):
    discussion = Discussion.objects.get(id=pk)
    form = DiscussionForm(instance=discussion)

    if request.user != discussion.host:
        messages.error(request, 'You don\'t have permission to edit this discussion.')
        return redirect('home')

    if request.method == 'POST':
        form = DiscussionForm(request.POST, instance=discussion)
        if form.is_valid():
            form.save()
            return redirect('home')

        context = {'form': form}
        return render(request, 'base/discussion_form.html', context)
    else:
        form = DiscussionForm(instance=discussion)
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


def get_popular_tags():
    time_threshold = datetime.now() - timedelta(days=30)
    popular_tags = (
        # TaggedItem.objects.filter(discussion__created_at__gte=time_threshold)
        TaggedItem.objects.filter(
            content_type__model='discussion',  # Filter by the Discussion model
            object_id__in=Discussion.objects.filter(created_at__gte=time_threshold).values('id')
        )
        .values('tag__name', 'tag__slug').annotate(tag_count=Count('tag')).order_by('tag_count')
    )
    popular_tags = popular_tags[:3]
    return popular_tags
