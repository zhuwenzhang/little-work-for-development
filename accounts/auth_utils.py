from functools import wraps

from django.shortcuts import redirect

from .models import UserApp


SESSION_USER_ID = "login_user_id"


def get_current_user(request):
    user_id = request.session.get(SESSION_USER_ID)
    if not user_id:
        return None
    try:
        user = UserApp.objects.get(pk=user_id)
    except UserApp.DoesNotExist:
        request.session.flush()
        return None
    if not user.is_active_user:
        request.session.flush()
        return None
    return user


def login_user(request, user: UserApp):
    request.session[SESSION_USER_ID] = user.user_id
    request.session.cycle_key()


def logout_user(request):
    request.session.flush()


def login_required_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            return redirect("accounts:login")
        request.cms_user = user
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            return redirect("accounts:login")
        if not user.is_admin_side:
            return redirect("cms:home")
        request.cms_user = user
        return view_func(request, *args, **kwargs)

    return wrapper


def super_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            return redirect("accounts:login")
        if user.user_type != UserApp.USER_TYPE_SUPER:
            return redirect("cms:admin_home")
        request.cms_user = user
        return view_func(request, *args, **kwargs)

    return wrapper
