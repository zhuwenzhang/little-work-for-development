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


class Comment(models.Model):
    """评论表：is_hidden=0 显示，1 删除/不可见。"""

    STATUS_SHOW = 0
    STATUS_HIDDEN = 1
    STATUS_CHOICES = (
        (STATUS_SHOW, "显示"),
        (STATUS_HIDDEN, "删除"),
    )

    user = models.ForeignKey(
        "accounts.UserApp",
        to_field="user_id",
        db_column="user_id",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="用户ID",
    )
    item = models.ForeignKey(
        Item,
        db_column="item_id",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="文章ID",
    )
    content = models.CharField("评论内容", max_length=100)
    commented_at = models.DateTimeField("评论时间", auto_now_add=True)
    is_hidden = models.SmallIntegerField(
        "是否显示", choices=STATUS_CHOICES, default=STATUS_SHOW
    )
    # 冗余存储用户姓名，便于按作业要求作为评论表字段使用
    user_name = models.CharField("用户姓名", max_length=30)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "comment"
        verbose_name = "评论"
        verbose_name_plural = "评论"
        ordering = ["-commented_at", "-id"]

    def __str__(self):
        return f"{self.user_name}: {self.content[:20]}"

    @property
    def item_title_short(self):
        title = self.item.title if self.item_id else ""
        return title[:5] if title else ""
