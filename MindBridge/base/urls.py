from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('discussion/<str:pk>/', views.discussion, name='discussion'),
    path('create-discussion/', views.create_discussion, name='create-discussion'),
    path('update-discussion/<str:pk>/', views.update_discussion, name='update-discussion'),
    path('delete-discussion/<str:pk>/', views.delete_discussion, name='delete-discussion'),
]
