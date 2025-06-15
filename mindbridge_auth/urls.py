from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    path('sign-up/', views.signup_page, name='sign-up'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('success/', views.success, name='success'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('sign-up-company/', views.sign_up_company, name='sign-up-company'),
    path('reset-password/', views.reset_password, name='reset-password'),
    path('reset-password-done/', views.reset_password_done, name='reset-password-done')
]
