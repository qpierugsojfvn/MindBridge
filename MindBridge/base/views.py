from django.shortcuts import render, redirect
from django.db.models import Q
from taggit.models import Tag

from .models import *
from .forms import DiscussionForm


def home(request):
    q = request.GET.get('q', '')
    if q:
        discussions = Discussion.objects.filter(
            Q(tags__name__icontains=q) |
            Q(title__icontains=q) |
            Q(content__icontains=q)
        ).distinct()
    else:
        discussions = Discussion.objects.all()

    tags = Tag.objects.all()

    context = {'discussions': discussions, 'tags': tags}
    return render(request, 'base/home.html', context)


def discussion(request, pk):
    discussion = Discussion.objects.get(id=pk)
    context = {'discussion': discussion}
    return render(request, 'base/discussion.html', context)


def create_discussion(request):
    form = DiscussionForm()

    if request.method == 'POST':
        form = DiscussionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/discussion_form.html', context)


def update_discussion(request, pk):
    discussion = Discussion.objects.get(id=pk)
    form = DiscussionForm(instance=discussion)
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


def delete_discussion(request, pk):
    discussion = Discussion.objects.get(id=pk)
    if request.method == 'POST':
        discussion.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': discussion})
