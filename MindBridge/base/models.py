from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager


class Discussion(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    # participants=
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tags = TaggableManager()

    class Meta:
        ordering = ['-updated_at', '-created_at']


    def __str__(self):
        return self.title


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content[0:50]
