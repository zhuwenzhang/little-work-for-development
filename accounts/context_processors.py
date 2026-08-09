from .auth_utils import get_current_user


def current_user(request):
    return {"cms_user": get_current_user(request)}
