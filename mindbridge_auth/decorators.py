from django.http import HttpResponseForbidden
from functools import wraps
from mindbridge_auth.models import UserProfile


def role_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden()

            user = request.user
            user_profile, created = UserProfile.objects.get_or_create(user=user)  # Распаковываем кортеж

            if user_profile.role not in roles:
                return HttpResponseForbidden()
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator