from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Application


@receiver(post_save, sender=Application)
def send_application_notification(sender, instance, created, **kwargs):
    if created:
        # Email to applicant
        send_mail(
            'Application Submitted',
            f'Your application for {instance.vacancy.title} has been received.',
            'noreply@yourdomain.com',
            [instance.applicant.email],
            fail_silently=False,
        )

        # Email to company
        send_mail(
            'New Application Received',
            f'A new application has been submitted for {instance.vacancy.title}.',
            'noreply@yourdomain.com',
            [instance.vacancy.company.user.email],
            fail_silently=False,
        )
