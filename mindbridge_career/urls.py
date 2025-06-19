# careers/urls.py
from django.urls import path
from . import views

app_name = 'careers'

urlpatterns = [
    path('', views.vacancy_list, name='vacancy_list'),
    path('<int:pk>/', views.vacancy_detail, name='vacancy_detail'),
    path('post/', views.post_vacancy, name='post_vacancy'),
    path('vacancies/<int:pk>/deactivate/', views.deactivate_vacancy, name='deactivate_vacancy'),
    path('<int:pk>/apply/', views.apply_vacancy, name='apply_vacancy'),
    # path('application/<int:pk>/', views.application_status, name='application_status'),
    path('dashboard/', views.company_dashboard, name='company_dashboard'),
    path('vacancy/toggle/<int:pk>/', views.toggle_vacancy, name='toggle_vacancy'),
    path('application/<int:pk>/status/', views.update_application_status, name='update_application_status'),
    path('application/<int:pk>/', views.application_detail, name='application_detail'),
]

# from django.urls import path
# from . import views
#
# app_name = 'careers'
#
# urlpatterns = [
#     # Public views
#     path('', views.vacancy_list, name='vacancy_list'),
#     path('vacancy/<int:pk>/', views.vacancy_detail, name='vacancy_detail'),
#
#     # Company management
#     path('company/create/', views.create_company, name='create_company'),
#     path('my-companies/', views.my_companies, name='my_companies'),
#
#     # Vacancy management
#     path('vacancy/create/', views.create_vacancy, name='create_vacancy'),
#     path('manage-vacancies/', views.manage_vacancies, name='manage_vacancies'),
#
#     # Application flow
#     path('vacancy/<int:pk>/apply/', views.apply_vacancy, name='apply_vacancy'),
#     path('my-applications/', views.my_applications, name='my_applications'),
# ]
