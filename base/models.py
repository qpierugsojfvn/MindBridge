from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from taggit.models import TagBase, GenericTaggedItemBase, TaggedItem
from .utils import *


class CustomTag(TagBase):
    # Override the slug field to use custom slugify
    slug = models.SlugField(unique=True, max_length=100, allow_unicode=True)

    def save(self, *args, **kwargs):
        # Use the custom slugify function
        self.slug = custom_slugify_(self.name)
        super().save(*args, **kwargs)

class TaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(
        CustomTag,
        related_name="%(app_label)s_%(class)s_items",
        on_delete=models.CASCADE,
    )

class Discussion(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    participants=models.ManyToManyField(User, related_name='participants', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # tags = TaggableManager()
    tags = TaggableManager(through=TaggedItem, blank=True)
    tagged_items = GenericRelation(TaggedItem, related_query_name='discussion')

    class Meta:
        ordering = ['-updated_at', '-created_at']


    def __str__(self):
        return self.title


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content[0:50]
