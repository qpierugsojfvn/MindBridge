from django.urls import path
from . import views

app_name = 'careers'

urlpatterns = [
    # Public views
    path('', views.vacancy_list, name='vacancy_list'),
    path('vacancy/<int:pk>/', views.vacancy_detail, name='vacancy_detail'),

    # Company management
    path('company/create/', views.create_company, name='create_company'),
    path('my-companies/', views.my_companies, name='my_companies'),

    # Vacancy management
    path('vacancy/create/', views.create_vacancy, name='create_vacancy'),
    path('manage-vacancies/', views.manage_vacancies, name='manage_vacancies'),

    # Application flow
    path('vacancy/<int:pk>/apply/', views.apply_vacancy, name='apply_vacancy'),
    path('my-applications/', views.my_applications, name='my_applications'),
]
