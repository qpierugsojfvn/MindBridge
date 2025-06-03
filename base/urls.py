from django.urls import path
from . import views
from .views import TagAutocompleteView

app_name = 'base'

urlpatterns = [
    # path('auth-receiver', views.auth_receiver, name='auth-receiver'),
    path('', views.home, name='home'),
    path('discussion/<str:pk>/', views.discussion, name='discussion'),
    path('user-profile/<str:pk>/', views.user_profile, name='user-profile'),
    path('edit-profile/<str:pk>/', views.edit_profile, name='edit-profile'),
    path('load-cities/', views.load_cities, name='load-cities'),
    path('create-discussion/', views.create_discussion, name='create-discussion'),
    path('update-discussion/<str:pk>/', views.update_discussion, name='update-discussion'),
    path('delete-discussion/<str:pk>/', views.delete_discussion, name='delete-discussion'),
    path('delete-answer/<str:pk>/', views.delete_answer, name='delete-answer'),
    path('api/tags/', TagAutocompleteView.as_view(), name='tags-autocomplete'),
    path('view-discussion', views.view_discussion, name='view-discussion'),
]
