from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from base.decorators import user_not_authenticated
from base.forms import UserRegistrationForm
from base.tokens import account_activation_token


# Create your views here.
def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('base:home')
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
            return redirect('base:home')
        else:
            messages.error(request, 'Invalid username or password.')
    context = {'page': page}
    return render(request, 'login_signup.html', context)


def logout_page(request):
    logout(request)
    return redirect('base:home')


def success(request):
    return redirect('base:home')


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
        return redirect('auth:login')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('base:home')

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
                return render(request, 'login_signup.html', {'page': page, 'form': form})

            user = form.save(commit=False)
            user.username = user.username.lower()
            user.is_active = False
            user.save()

            if not activateEmail(request, user, email):
                return render(request, 'login_signup.html', {'page': page, 'form': form})

            return redirect('auth:login')  # Redirect to login after successful signup

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    context = {'page': page, 'form': form}
    return render(request, 'login_signup.html', context)
