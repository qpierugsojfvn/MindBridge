from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import User
from base.models import City
from base.models import Country
from django.dispatch import receiver
from django.db.models.signals import post_save


class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('COMPANY', 'Company'),
        ('EMPLOYEE', 'Employee'),
        ('ADMIN', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    about = models.TextField(max_length=500, blank=True)
    bio = models.TextField(max_length=50, blank=True)
    # todo скрыть от юзера эти поля(только для компаний)
    company_name = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text="Upload a square profile picture (max 2MB)",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )
    cover_photo = models.ImageField(
        upload_to='cover_photos/',
        null=True,
        blank=True,
        help_text="Upload a wide cover photo (recommended ratio 3:1, max 2MB)",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )
    interests = models.ManyToManyField(Interest, blank=True)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)
    portfolio_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Portfolio (Behance, Dribbble, etc.)"
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return '/static/images/default_avatar.png'

    def get_cover_photo_url(self):
        if self.cover_photo and hasattr(self.cover_photo, 'url'):
            return self.cover_photo.url
        return None

    def save(self, *args, **kwargs):
        try:
            old = UserProfile.objects.get(pk=self.pk)
            if old.avatar and old.avatar != self.avatar:
                old.avatar.delete(save=False)
            if old.cover_photo and old.cover_photo != self.cover_photo:
                old.cover_photo.delete(save=False)
        except UserProfile.DoesNotExist:
            pass
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
