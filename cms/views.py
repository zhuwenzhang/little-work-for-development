from datetime import datetime, time

from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_http_methods, require_POST

from accounts.auth_utils import admin_required, get_current_user, login_required_custom
from accounts.models import UserApp

from .models import Category, Item


def _parse_day_range(date_from_str, date_to_str):
    """把日期字符串转成带时区的起止时间。"""
    start = None
    end = None
    d1 = parse_date(date_from_str) if date_from_str else None
    d2 = parse_date(date_to_str) if date_to_str else None
    if d1:
        start = timezone.make_aware(datetime.combine(d1, time.min))
    if d2:
        end = timezone.make_aware(datetime.combine(d2, time.max))
    return start, end


@login_required_custom
def home(request):
    """普通用户前台：文章列表 + 三种查询。"""
    user = request.cms_user
    if user.is_admin_side:
        return redirect("cms:admin_home")

    mode = (request.GET.get("mode") or "title").strip()
    keyword = (request.GET.get("keyword") or "").strip()
    date_from = (request.GET.get("date_from") or "").strip()
    date_to = (request.GET.get("date_to") or "").strip()
    category_id = (request.GET.get("category_id") or "").strip()

    items = Item.objects.filter(is_published=True).select_related("category")
    searched = any(request.GET.get(k) for k in ("mode", "keyword", "date_from", "date_to", "category_id"))

    if mode == "title" and keyword:
        items = items.filter(title__icontains=keyword)
    elif mode == "time":
        start, end = _parse_day_range(date_from, date_to)
        if start:
            items = items.filter(published_at__gte=start)
        if end:
            items = items.filter(published_at__lte=end)
    elif mode == "category" and category_id:
        items = items.filter(category_id=category_id)

    categories = Category.objects.all()
    return render(
        request,
        "cms/home.html",
        {
            "items": items,
            "categories": categories,
            "mode": mode,
            "keyword": keyword,
            "date_from": date_from,
            "date_to": date_to,
            "category_id": category_id,
            "searched": searched,
        },
    )


@login_required_custom
def item_detail(request, pk):
    user = request.cms_user
    item = get_object_or_404(Item.objects.select_related("category"), pk=pk)
    if not item.is_published and not user.is_admin_side:
        return redirect("cms:home")
    return render(request, "cms/item_detail.html", {"item": item})


@admin_required
def admin_home(request):
    stats = {
        "category_count": Category.objects.count(),
        "item_count": Item.objects.count(),
        "published_count": Item.objects.filter(is_published=True).count(),
        "user_count": UserApp.objects.count(),
    }
    return render(request, "cms/admin_home.html", {"stats": stats})


# ---------- 栏目 CRUD ----------
@admin_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, "cms/category_list.html", {"categories": categories})


@admin_required
@require_http_methods(["GET", "POST"])
def category_create(request):
    if request.method == "GET":
        return render(request, "cms/category_form.html", {"mode": "create", "category": None})

    name = (request.POST.get("name") or "").strip()
    description = (request.POST.get("description") or "").strip()
    if not name:
        return render(
            request,
            "cms/category_form.html",
            {"mode": "create", "category": None, "error": "栏目名称不能为空", "form": {"name": name, "description": description}},
        )
    if Category.objects.filter(name=name).exists():
        return render(
            request,
            "cms/category_form.html",
            {"mode": "create", "category": None, "error": "栏目名称已存在", "form": {"name": name, "description": description}},
        )
    Category.objects.create(name=name, description=description)
    return redirect("cms:category_list")


@admin_required
@require_http_methods(["GET", "POST"])
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "GET":
        return render(request, "cms/category_form.html", {"mode": "edit", "category": category})

    name = (request.POST.get("name") or "").strip()
    description = (request.POST.get("description") or "").strip()
    if not name:
        return render(
            request,
            "cms/category_form.html",
            {"mode": "edit", "category": category, "error": "栏目名称不能为空"},
        )
    if Category.objects.filter(name=name).exclude(pk=pk).exists():
        return render(
            request,
            "cms/category_form.html",
            {"mode": "edit", "category": category, "error": "栏目名称已存在"},
        )
    category.name = name
    category.description = description
    category.save()
    return redirect("cms:category_list")


@admin_required
@require_POST
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect("cms:category_list")


# ---------- 文章 CRUD ----------
@admin_required
def item_list(request):
    items = Item.objects.select_related("category").all()
    return render(request, "cms/item_list.html", {"items": items})


def _item_form_context(mode, item=None, error=None, post=None):
    categories = Category.objects.all()
    form = {}
    if post is not None:
        form = {
            "title": (post.get("title") or "").strip(),
            "content": (post.get("content") or "").strip(),
            "category_id": (post.get("category_id") or "").strip(),
            "author": (post.get("author") or "").strip(),
            "published_at": (post.get("published_at") or "").strip(),
            "is_published": post.get("is_published") == "1",
        }
    elif item is not None:
        form = {
            "title": item.title,
            "content": item.content,
            "category_id": str(item.category_id),
            "author": item.author,
            "published_at": timezone.localtime(item.published_at).strftime("%Y-%m-%dT%H:%M"),
            "is_published": item.is_published,
        }
    return {
        "mode": mode,
        "item": item,
        "categories": categories,
        "form": form,
        "error": error,
    }


@admin_required
@require_http_methods(["GET", "POST"])
def item_create(request):
    if request.method == "GET":
        ctx = _item_form_context("create")
        ctx["form"] = {
            "title": "",
            "content": "",
            "category_id": "",
            "author": request.cms_user.name,
            "published_at": timezone.localtime().strftime("%Y-%m-%dT%H:%M"),
            "is_published": True,
        }
        return render(request, "cms/item_form.html", ctx)

    ctx = _item_form_context("create", post=request.POST)
    form = ctx["form"]
    if not form["title"] or not form["content"] or not form["category_id"]:
        ctx["error"] = "标题、正文、栏目均为必填"
        return render(request, "cms/item_form.html", ctx)

    category = get_object_or_404(Category, pk=form["category_id"])
    published_at = timezone.now()
    if form["published_at"]:
        try:
            published_at = timezone.make_aware(datetime.strptime(form["published_at"], "%Y-%m-%dT%H:%M"))
        except ValueError:
            ctx["error"] = "发表时间格式不正确"
            return render(request, "cms/item_form.html", ctx)

    Item.objects.create(
        title=form["title"],
        content=form["content"],
        category=category,
        author=form["author"][:30],
        published_at=published_at,
        is_published=form["is_published"],
    )
    return redirect("cms:item_list")


@admin_required
@require_http_methods(["GET", "POST"])
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == "GET":
        return render(request, "cms/item_form.html", _item_form_context("edit", item=item))

    ctx = _item_form_context("edit", item=item, post=request.POST)
    form = ctx["form"]
    if not form["title"] or not form["content"] or not form["category_id"]:
        ctx["error"] = "标题、正文、栏目均为必填"
        return render(request, "cms/item_form.html", ctx)

    category = get_object_or_404(Category, pk=form["category_id"])
    published_at = item.published_at
    if form["published_at"]:
        try:
            published_at = timezone.make_aware(datetime.strptime(form["published_at"], "%Y-%m-%dT%H:%M"))
        except ValueError:
            ctx["error"] = "发表时间格式不正确"
            return render(request, "cms/item_form.html", ctx)

    item.title = form["title"]
    item.content = form["content"]
    item.category = category
    item.author = form["author"][:30]
    item.published_at = published_at
    item.is_published = form["is_published"]
    item.save()
    return redirect("cms:item_list")


@admin_required
@require_POST
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item.delete()
    return redirect("cms:item_list")


# ---------- 用户管理 ----------
@admin_required
def user_list(request):
    current = request.cms_user
    users = UserApp.objects.all().order_by("user_type", "user_id")
    return render(
        request,
        "cms/user_list.html",
        {
            "users": users,
            "can_manage_admin": current.user_type == UserApp.USER_TYPE_SUPER,
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def user_create(request):
    current = request.cms_user
    can_manage_admin = current.user_type == UserApp.USER_TYPE_SUPER
    type_choices = [(UserApp.USER_TYPE_NORMAL, "普通用户")]
    if can_manage_admin:
        type_choices.append((UserApp.USER_TYPE_ADMIN, "管理员"))

    if request.method == "GET":
        return render(
            request,
            "cms/user_form.html",
            {"type_choices": type_choices, "form": {"user_id": "", "password": "", "name": "", "user_type": "1"}},
        )

    user_id = (request.POST.get("user_id") or "").strip()
    password = (request.POST.get("password") or "").strip()
    name = (request.POST.get("name") or "").strip()
    user_type_raw = (request.POST.get("user_type") or "1").strip()
    form = {"user_id": user_id, "password": password, "name": name, "user_type": user_type_raw}

    try:
        user_type = int(user_type_raw)
    except ValueError:
        user_type = UserApp.USER_TYPE_NORMAL

    allowed_types = {UserApp.USER_TYPE_NORMAL}
    if can_manage_admin:
        allowed_types.add(UserApp.USER_TYPE_ADMIN)

    if user_type not in allowed_types:
        return render(
            request,
            "cms/user_form.html",
            {"type_choices": type_choices, "form": form, "error": "无权创建该类型用户"},
        )
    if not user_id or not password or not name:
        return render(
            request,
            "cms/user_form.html",
            {"type_choices": type_choices, "form": form, "error": "请填写完整信息"},
        )
    if len(user_id) > 15 or len(password) > 30 or len(name) > 30:
        return render(
            request,
            "cms/user_form.html",
            {"type_choices": type_choices, "form": form, "error": "字段长度超出限制"},
        )
    if UserApp.objects.filter(pk=user_id).exists():
        return render(
            request,
            "cms/user_form.html",
            {"type_choices": type_choices, "form": form, "error": "用户ID已存在"},
        )

    UserApp.objects.create(
        user_id=user_id,
        password=password,
        name=name,
        user_type=user_type,
        is_disabled=UserApp.STATUS_ACTIVE,
    )
    return redirect("cms:user_list")


@admin_required
@require_POST
def user_toggle(request, user_id):
    current = request.cms_user
    target = get_object_or_404(UserApp, pk=user_id)

    if target.user_id == current.user_id:
        return redirect("cms:user_list")

    # 超级用户：可停用普通用户和管理员；不可动其他超级用户
    # 管理员：只能停用普通用户
    if current.user_type == UserApp.USER_TYPE_SUPER:
        if target.user_type == UserApp.USER_TYPE_SUPER:
            return redirect("cms:user_list")
    elif current.user_type == UserApp.USER_TYPE_ADMIN:
        if target.user_type != UserApp.USER_TYPE_NORMAL:
            return redirect("cms:user_list")
    else:
        return redirect("cms:user_list")

    target.is_disabled = (
        UserApp.STATUS_ACTIVE
        if target.is_disabled == UserApp.STATUS_DISABLED
        else UserApp.STATUS_DISABLED
    )
    target.save(update_fields=["is_disabled", "updated_at"])
    return redirect("cms:user_list")
