from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .auth_utils import get_current_user, login_user, logout_user
from .models import UserApp


@require_http_methods(["GET", "POST"])
def register(request):
    if get_current_user(request):
        return redirect("cms:home")

    context = {"form": {"user_id": "", "password": "", "name": ""}}
    if request.method == "GET":
        return render(request, "accounts/register.html", context)

    user_id = (request.POST.get("user_id") or "").strip()
    password = (request.POST.get("password") or "").strip()
    name = (request.POST.get("name") or "").strip()
    context["form"] = {"user_id": user_id, "password": password, "name": name}

    if not user_id or not password or not name:
        context["error"] = "请填写用户ID、密码和姓名"
        return render(request, "accounts/register.html", context)
    if len(user_id) > 15:
        context["error"] = "用户ID不能超过15个字符"
        return render(request, "accounts/register.html", context)
    if len(password) > 30:
        context["error"] = "密码不能超过30个字符"
        return render(request, "accounts/register.html", context)
    if len(name) > 30:
        context["error"] = "姓名不能超过30个字符"
        return render(request, "accounts/register.html", context)
    if UserApp.objects.filter(pk=user_id).exists():
        context["error"] = "用户ID已存在，请重新注册"
        return render(request, "accounts/register.html", context)

    try:
        UserApp.objects.create(
            user_id=user_id,
            password=password,
            name=name,
            user_type=UserApp.USER_TYPE_NORMAL,
            is_disabled=UserApp.STATUS_ACTIVE,
        )
    except IntegrityError:
        context["error"] = "用户ID已存在，请重新注册"
        return render(request, "accounts/register.html", context)

    context["success"] = "注册成功，0.5秒后跳转到登录界面"
    context["redirect_url"] = "/login/"
    return render(request, "accounts/register.html", context)


@require_http_methods(["GET", "POST"])
def login_view(request):
    current = get_current_user(request)
    if current:
        if current.is_admin_side:
            return redirect("cms:admin_home")
        return redirect("cms:home")

    context = {"form": {"user_id": "", "password": ""}}
    if request.method == "GET":
        return render(request, "accounts/login.html", context)

    user_id = (request.POST.get("user_id") or "").strip()
    password = (request.POST.get("password") or "").strip()
    context["form"] = {"user_id": user_id, "password": password}

    if not user_id or not password:
        context["error"] = "请输入用户ID和密码"
        return render(request, "accounts/login.html", context)

    try:
        user = UserApp.objects.get(pk=user_id)
    except UserApp.DoesNotExist:
        context["error"] = "用户ID不存在，请先注册"
        context["redirect_url"] = "/register/"
        return render(request, "accounts/login.html", context)

    if user.password != password:
        context["error"] = "密码错误"
        return render(request, "accounts/login.html", context)

    if not user.is_active_user:
        context["error"] = "该账号已停用，无法登录"
        return render(request, "accounts/login.html", context)

    # 按数据库中的用户类型跳转对应界面
    login_user(request, user)
    if user.is_admin_side:
        return redirect("cms:admin_home")
    return redirect("cms:home")


def logout_view(request):
    logout_user(request)
    return redirect("accounts:login")
