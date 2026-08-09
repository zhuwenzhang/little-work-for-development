from django.db import models


class UserApp(models.Model):
    USER_TYPE_ADMIN = 0
    USER_TYPE_NORMAL = 1
    USER_TYPE_SUPER = 2
    USER_TYPE_CHOICES = (
        (USER_TYPE_ADMIN, "管理员"),
        (USER_TYPE_NORMAL, "普通用户"),
        (USER_TYPE_SUPER, "超级用户"),
    )

    STATUS_ACTIVE = 0
    STATUS_DISABLED = 1
    STATUS_CHOICES = (
        (STATUS_ACTIVE, "正常"),
        (STATUS_DISABLED, "停用"),
    )

    user_id = models.CharField("用户ID", max_length=15, primary_key=True)
    password = models.CharField("密码", max_length=30)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    user_type = models.SmallIntegerField(
        "用户类型", choices=USER_TYPE_CHOICES, default=USER_TYPE_NORMAL
    )
    is_disabled = models.SmallIntegerField(
        "是否停用", choices=STATUS_CHOICES, default=STATUS_ACTIVE
    )
    name = models.CharField("用户姓名", max_length=30)
    updated_at = models.DateTimeField("最近更新时间", auto_now=True)

    class Meta:
        db_table = "user_app"
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return f"{self.user_id}({self.name})"

    @property
    def is_active_user(self):
        return self.is_disabled == self.STATUS_ACTIVE

    @property
    def is_admin_side(self):
        return self.user_type in (self.USER_TYPE_ADMIN, self.USER_TYPE_SUPER)

    @property
    def user_type_label(self):
        return dict(self.USER_TYPE_CHOICES).get(self.user_type, "未知")
