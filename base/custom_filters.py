from django import template
import random

register = template.Library()

@register.filter
def random_items(queryset, count=5):
    items = list(queryset)
    random.shuffle(items)
    return items[:int(count)]