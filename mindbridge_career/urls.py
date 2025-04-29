from django.urls import path
from . import views

app_name = 'careers'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/apply/', views.apply_to_job, name='apply'),
]
