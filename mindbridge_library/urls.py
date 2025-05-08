from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='library'),
    path('articles/', views.index, name='filter_articles'),
    path('videos/', views.index, name='filter_videos'),
    path('create/', views.create_lesson, name='create_lesson'),
    path('<slug:slug>/edit/', views.update_lesson, name='update_lesson'),
    path('<slug:slug>/', views.lesson_detail, name='lesson_detail'),
    path('<slug:slug>/add-attachment/', views.add_attachment, name='add_attachment'),
    path('<slug:slug>/update-progress/', views.update_progress, name='update_progress'),
]
