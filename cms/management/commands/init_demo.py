from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import UserApp
from cms.models import Category, Item


class Command(BaseCommand):
    help = "初始化演示账号、栏目和文章"

    def handle(self, *args, **options):
        super_user, _ = UserApp.objects.update_or_create(
            user_id="super",
            defaults={
                "password": "1",
                "name": "超级管理员",
                "user_type": UserApp.USER_TYPE_SUPER,
                "is_disabled": UserApp.STATUS_ACTIVE,
            },
        )
        admin_user, _ = UserApp.objects.update_or_create(
            user_id="admin",
            defaults={
                "password": "1",
                "name": "管理员",
                "user_type": UserApp.USER_TYPE_ADMIN,
                "is_disabled": UserApp.STATUS_ACTIVE,
            },
        )
        normal_user, _ = UserApp.objects.update_or_create(
            user_id="user01",
            defaults={
                "password": "1",
                "name": "张三",
                "user_type": UserApp.USER_TYPE_NORMAL,
                "is_disabled": UserApp.STATUS_ACTIVE,
            },
        )

        news, _ = Category.objects.get_or_create(
            name="校园新闻",
            defaults={"description": "学校新闻动态"},
        )
        notice, _ = Category.objects.get_or_create(
            name="通知公告",
            defaults={"description": "重要通知"},
        )

        if not Item.objects.exists():
            Item.objects.create(
                title="开学典礼顺利举行",
                content="本学期开学典礼于今日举行，师生共同迎接新学期。",
                category=news,
                author=admin_user.name,
                published_at=timezone.now(),
                is_published=True,
            )
            Item.objects.create(
                title="图书馆开放时间调整通知",
                content="自下周起，图书馆工作日开放时间调整为 8:00-22:00。",
                category=notice,
                author=super_user.name,
                published_at=timezone.now(),
                is_published=True,
            )
            Item.objects.create(
                title="草稿：未发布示例",
                content="这是一篇未发布的草稿，普通用户前台不可见。",
                category=news,
                author=admin_user.name,
                published_at=timezone.now(),
                is_published=False,
            )

        self.stdout.write(self.style.SUCCESS("演示数据初始化完成"))
        self.stdout.write("超级用户: super / 1")
        self.stdout.write("管理员:   admin / 1")
        self.stdout.write(f"普通用户: {normal_user.user_id} / 1")
