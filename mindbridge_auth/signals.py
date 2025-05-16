
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from base.models import UserProfile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created and not UserProfile.objects.filter(user=instance).exists():
        UserProfile.objects.create(user=instance)
