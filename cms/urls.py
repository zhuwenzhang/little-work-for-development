from django.urls import path

from . import views

app_name = "cms"

urlpatterns = [
    path("", views.home, name="home"),
    path("item/<int:pk>/", views.item_detail, name="item_detail"),
    path("manage/", views.admin_home, name="admin_home"),
    path("manage/categories/", views.category_list, name="category_list"),
    path("manage/categories/create/", views.category_create, name="category_create"),
    path("manage/categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("manage/categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
    path("manage/items/", views.item_list, name="item_list"),
    path("manage/items/create/", views.item_create, name="item_create"),
    path("manage/items/<int:pk>/edit/", views.item_edit, name="item_edit"),
    path("manage/items/<int:pk>/delete/", views.item_delete, name="item_delete"),
    path("manage/users/", views.user_list, name="user_list"),
    path("manage/users/create/", views.user_create, name="user_create"),
    path("manage/users/<str:user_id>/toggle/", views.user_toggle, name="user_toggle"),
]
