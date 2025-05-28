# careers/middleware.py
from django.shortcuts import redirect
from django.urls import reverse


class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Исключения для статических файлов и API
        excluded_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/favicon.ico',
            '/api/',
        ]

        if any(request.path.startswith(path) for path in excluded_paths):
            return self.get_response(request)

        if request.user.is_authenticated:
            try:
                # Проверяем существование URL перед использованием
                try:
                    complete_profile_url = reverse('careers:complete_profile')
                except:
                    complete_profile_url = '/career/complete-profile/'

                if not hasattr(request.user, 'profile') and not request.path == complete_profile_url:
                    return redirect(complete_profile_url)
            except Exception as e:
                # Логируем ошибку, но не прерываем запрос
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"ProfileCompletionMiddleware error: {str(e)}")

        return self.get_response(request)