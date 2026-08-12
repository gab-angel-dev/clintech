# accounts/decorators.py
from functools import wraps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import resolve_url
from django_htmx.http import HttpResponseClientRedirect


def htmx_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        login_url = resolve_url(settings.LOGIN_URL)

        if getattr(request, 'htmx', False):
            return HttpResponseClientRedirect(login_url)

        return login_required(view_func)(request, *args, **kwargs)

    return wrapper