from django.urls import path
from . import views
from .views import TagAutocompleteView

app_name = 'base'

urlpatterns = [
    # path('auth-receiver', views.auth_receiver, name='auth-receiver'),
    path('', views.home, name='home'),
    path('discussion/<str:pk>/', views.discussion, name='discussion'),
    path('discussions/', views.discussions, name='discussions'),
    path('user-profile/<str:pk>/', views.user_profile, name='user-profile'),
    path('edit-profile/<str:pk>/', views.edit_profile, name='edit-profile'),
    path('load-cities/', views.load_cities, name='load-cities'),
    path('create-discussion/', views.create_discussion, name='create-discussion'),
    path('update-discussion/<str:pk>/', views.update_discussion, name='update-discussion'),
    path('delete-discussion/<str:pk>/', views.delete_discussion, name='delete-discussion'),
    path('delete-answer/<str:pk>/', views.delete_answer, name='delete-answer'),
    path('save-discussion/<int:pk>/', views.save_discussion, name='save-discussion'),
    path('report-discussion/<int:pk>/', views.report_discussion, name='report-discussion'),
    path('api/tags/', TagAutocompleteView.as_view(), name='tags-autocomplete'),
    path('view-discussion', views.view_discussion, name='view-discussion'),
    path('saved/', views.saved_discussions, name='saved-discussions'),
    path('reported/', views.reported_discussions, name='reported-discussions'),
    path('resolve-report/<int:pk>/', views.resolve_report, name='resolve-report'),
    path('create-answer', views.create_answer, name='create-answer'),
    path('answer/<int:pk>/', views.answer_discussion, name='answer-discussion'),
    path('answer/<int:pk>/reply/', views.create_reply, name='create-reply'),
    path('save-answer/<int:pk>/', views.save_answer, name='save-answer'),
    path('report-answer/<int:pk>/', views.report_answer, name='report-answer'),
]
