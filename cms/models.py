from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField("栏目名称", max_length=100, unique=True)
    description = models.CharField("简介", max_length=255, blank=True, default="")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "category"
        verbose_name = "栏目"
        verbose_name_plural = "栏目"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Item(models.Model):
    title = models.CharField("标题", max_length=200)
    content = models.TextField("正文")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="所属栏目",
    )
    author = models.CharField("作者", max_length=30, blank=True, default="")
    published_at = models.DateTimeField("发表时间", default=timezone.now)
    is_published = models.BooleanField("是否发布", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "item"
        verbose_name = "文章"
        verbose_name_plural = "文章"
        ordering = ["-published_at", "-id"]

    def __str__(self):
        return self.title
