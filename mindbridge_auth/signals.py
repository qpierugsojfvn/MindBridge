
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from mindbridge_auth.models import UserProfile
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from allauth.account.signals import user_signed_up
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created and not UserProfile.objects.filter(user=instance).exists():
        UserProfile.objects.create(user=instance)

@receiver(user_signed_up)
def send_welcome_email(request, user, **kwargs):
    subject = 'Добро пожаловать!'
    message = render_to_string('welcome_email.html', {'user': user})
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
