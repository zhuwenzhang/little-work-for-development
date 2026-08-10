# -*- coding: utf-8 -*-
"""代码实现逻辑的设计.pdf — 与项目说明书同一排版标准。"""
from pathlib import Path

from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, PageBreak, Flowable

from pdf_kit import (
    ACCENT, TITLE, TEXT, MUTED, LINE, SOFT, WHITE,
    build_pdf, cover_block, toc_block, h1, h2, body, bullet, make_table,
)

OUT = Path(__file__).resolve().parent / "代码实现逻辑的设计.pdf"


class ArchDiagram(Flowable):
    def __init__(self, width=16.5 * cm, height=7.6 * cm):
        Flowable.__init__(self)
        self.box_width = width
        self.box_height = height

    def wrap(self, aw, ah):
        self.width = min(self.box_width, aw)
        self.height = self.box_height
        return self.width, self.height

    def _box(self, c, x, y, w, h, title, lines):
        c.setFillColor(WHITE)
        c.setStrokeColor(ACCENT)
        c.setLineWidth(1.25)
        c.roundRect(x, y, w, h, 5, fill=1, stroke=1)
        c.setFillColor(ACCENT)
        c.roundRect(x, y + h - 20, w, 20, 5, fill=1, stroke=0)
        c.rect(x, y + h - 20, w, 10, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("YaHeiBd", 9)
        c.drawCentredString(x + w / 2, y + h - 14, title)
        c.setFillColor(TEXT)
        c.setFont("YaHei", 8)
        ty = y + h - 34
        for line in lines:
            c.drawCentredString(x + w / 2, ty, line)
            ty -= 12

    def _arrow_down(self, c, x, y1, y2):
        c.setStrokeColor(ACCENT)
        c.setFillColor(ACCENT)
        c.setLineWidth(1.15)
        c.line(x, y1, x, y2 + 6)
        p = c.beginPath()
        p.moveTo(x, y2)
        p.lineTo(x - 4, y2 + 7)
        p.lineTo(x + 4, y2 + 7)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

    def draw(self):
        c = self.canv
        c.setFillColor(SOFT)
        c.setStrokeColor(LINE)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)

        cx = self.width / 2
        self._box(c, cx - 70, 195, 140, 48, "浏览器", ["页面请求 / 表单提交"])
        self._arrow_down(c, cx, 195, 172)
        self._box(c, cx - 95, 120, 190, 52, "config/urls.py", ["总路由分发"])
        self._arrow_down(c, cx, 120, 98)
        self._box(c, 30, 40, 175, 58, "accounts 应用", ["注册 / 登录 / 鉴权", "user_app"])
        self._box(c, self.width - 230, 40, 200, 58, "cms 应用", ["栏目/文章/评论/前台管理", "views + models"])

        c.setStrokeColor(ACCENT)
        c.setLineWidth(1.1)
        c.line(cx - 50, 120, 118, 98)
        c.line(cx + 50, 120, self.width - 130, 98)
        c.setFillColor(MUTED)
        c.setFont("YaHei", 7.5)
        c.drawString(20, 12, "templates 负责 HTML 渲染；static 提供 CSS；MySQL(cms_prototype) 被 models 读写。")


class LayerDiagram(Flowable):
    def __init__(self, width=16.5 * cm, height=5.8 * cm):
        Flowable.__init__(self)
        self.box_width = width
        self.box_height = height

    def wrap(self, aw, ah):
        self.width = min(self.box_width, aw)
        self.height = self.box_height
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(SOFT)
        c.setStrokeColor(LINE)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)

        layers = [
            ("templates / static", "页面结构与样式（HTML / CSS）"),
            ("views.py + urls.py", "路由分发、业务逻辑、权限判断"),
            ("models.py", "ORM 映射四张业务表"),
            ("MySQL cms_prototype", "user_app / category / item / comment"),
        ]
        y = self.height - 18
        for title, desc in layers:
            c.setFillColor(WHITE)
            c.setStrokeColor(ACCENT)
            c.setLineWidth(1.15)
            c.roundRect(18, y - 36, self.width - 36, 36, 5, fill=1, stroke=1)
            c.setFillColor(ACCENT)
            c.setFont("YaHeiBd", 9)
            c.drawString(30, y - 15, title)
            c.setFillColor(TEXT)
            c.setFont("YaHei", 8)
            c.drawString(30, y - 28, desc)
            y -= 44


def make_story(styles):
    story = []
    story.extend(cover_block(
        styles,
        "代码实现逻辑的设计",
        "点击目录可跳转；侧边书签亦可导航。",
        [
            "从目录结构、界面映射、视图实现到数据库表的代码级说明",
            "技术栈：Django MTV · MySQL 3307",
        ],
    ))
    story.append(PageBreak())
    story.extend(toc_block(styles))
    story.append(PageBreak())

    story.append(h1("第一章　总体架构", styles))
    story.append(body(
        "本项目基于 Django MTV（Model-Template-View）模式。浏览器请求先进入总路由，再分发到 "
        "<b>accounts</b>（账号）或 <b>cms</b>（业务）应用；视图读写 models，最后渲染 templates，样式来自 static。",
        styles,
    ))
    story.append(Spacer(1, 4))
    story.append(ArchDiagram())
    story.append(Paragraph("图 1　请求分发总览（带边框）", styles["Caption"]))

    story.append(body("分层实现关系：", styles, indent=False))
    story.append(LayerDiagram())
    story.append(Paragraph("图 2　代码分层（上展示、下存储）", styles["Caption"]))

    story.append(h1("第二章　目录职责说明", styles))
    story.append(make_table(
        ["目录/文件", "含义", "重点内容"],
        [
            ["config/", "项目配置中心", "settings.py 配库；urls.py 总路由；PyMySQL 接入"],
            ["accounts/", "账号应用", "user_app 模型；注册登录；session 鉴权"],
            ["cms/", "业务应用", "栏目/文章/评论；前台浏览；管理端 CRUD"],
            ["templates/", "HTML 模板", "登录注册、前台浏览、管理端各模块页面"],
            ["static/", "静态资源", "css/style.css 统一样式"],
            ["manage.py", "命令入口", "migrate / runserver / init_demo"],
            ["start.bat / stop.bat", "启停脚本", "MySQL(3307) + Django 一键启停"],
        ],
        [3.4 * cm, 3.4 * cm, 9.7 * cm], styles,
    ))

    story.append(h1("第三章　config：总开关", styles))
    story.append(h2("3.1 关键文件", styles))
    story.append(make_table(
        ["文件", "作用"],
        [
            ["settings.py", "数据库连接（3307/cms_prototype）、INSTALLED_APPS、模板与静态路径"],
            ["urls.py", "总路由：把请求分给 accounts.urls 与 cms.urls"],
            ["__init__.py", "pymysql.install_as_MySQLdb()，让 Django 使用 MySQL"],
        ],
        [3.5 * cm, 13 * cm], styles,
    ))
    story.append(body(
        "记忆点：改端口、库名、安装应用，优先看 <b>config/settings.py</b>；"
        "加新页面路由，先在应用 urls 写，再由 config 汇总。",
        styles,
    ))

    story.append(h1("第四章　accounts：登录注册与鉴权", styles))
    story.append(make_table(
        ["文件", "作用"],
        [
            ["models.py", "UserApp → 表 user_app（角色、停用、明文密码演示）"],
            ["auth_utils.py", "session 读写；login_required_custom / admin_required"],
            ["views.py", "register / login_view / logout_view"],
            ["urls.py", "/login/、/register/、/logout/"],
            ["context_processors.py", "模板中注入当前登录用户 cms_user"],
        ],
        [3.8 * cm, 12.7 * cm], styles,
    ))
    story.append(h2("4.1 界面对应", styles))
    story.append(make_table(
        ["界面", "模板", "视图", "功能"],
        [
            ["登录", "accounts/login.html", "login_view", "校验 user_app，按 user_type 跳前台/管理台"],
            ["注册", "accounts/register.html", "register", "仅注册普通用户；ID 冲突提示"],
            ["退出", "（无独立页）", "logout_view", "清空 session 回登录页"],
        ],
        [2.4 * cm, 4.4 * cm, 3.2 * cm, 6.5 * cm], styles,
    ))

    story.append(PageBreak())
    story.append(h1("第五章　cms：核心业务实现", styles))
    story.append(body(
        "cms 是内容与管理的主战场：<b>models.py</b> 定义三张业务表；<b>views.py</b> 实现前台与管理功能；"
        "<b>urls.py</b> 绑定路径；管理端页面统一套 <b>admin_base.html</b> 左右布局。",
        styles,
    ))

    story.append(h2("5.1 关键代码文件", styles))
    story.append(make_table(
        ["文件", "作用"],
        [
            ["models.py", "Category / Item / Comment"],
            ["views.py", "home、评论发表、栏目/文章/用户/评论管理"],
            ["urls.py", "前台与 /manage/... 管理路由"],
            ["management/commands/init_demo.py", "初始化演示账号与样例数据（可选）"],
        ],
        [5.2 * cm, 11.3 * cm], styles,
    ))

    story.append(h2("5.2 前台界面与代码对应", styles))
    story.append(make_table(
        ["界面/动作", "视图", "模板", "实现功能"],
        [
            ["文章浏览主界面", "home", "cms/home.html", "分栏、左标题右正文、题/时/作者查询、展示可见评论"],
            ["发表评论", "comment_create", "（home 内表单）", "POST 写入 comment，is_hidden=0"],
        ],
        [3.2 * cm, 3.2 * cm, 3.6 * cm, 6.5 * cm], styles,
    ))

    story.append(h2("5.3 管理端界面与代码对应", styles))
    story.append(body("布局壳：templates/cms/admin_base.html（左侧菜单 + 右侧内容区）", styles, indent=False))
    story.append(make_table(
        ["模块", "主要视图", "模板", "功能"],
        [
            ["概览", "admin_home", "admin_home.html", "栏目/文章/用户数量统计"],
            ["栏目管理", "category_list/create/edit/delete", "category_list.html<br/>category_form.html", "栏目增删改查"],
            ["文章管理", "item_list/create/edit/delete", "item_list.html<br/>item_form.html", "文章 CRUD；按题/时/作者查询"],
            ["用户管理", "user_list/create/toggle/reset_password", "user_list.html<br/>user_form.html", "新增用户；停用；初始化密码；按ID/姓名查"],
            ["评论管理", "comment_list/toggle", "comment_list.html", "按内容/姓名查；切换显示/隐藏"],
        ],
        [2.6 * cm, 4.6 * cm, 3.8 * cm, 5.5 * cm], styles,
    ))

    story.append(h2("5.4 公共页面与样式", styles))
    story.append(make_table(
        ["文件", "作用"],
        [
            ["templates/base.html", "全站页头、容器、自动跳转脚本"],
            ["templates/cms/admin_base.html", "管理端左侧导航高亮与右侧内容插槽"],
            ["static/css/style.css", "前台分栏、管理端侧栏、按钮描边、评论区等样式"],
        ],
        [5 * cm, 11.5 * cm], styles,
    ))

    story.append(h1("第六章　数据库与代码映射", styles))
    story.append(body(
        "业务库四张表由 models 映射。关系主线：<b>category 1—N item 1—N comment N—1 user_app</b>。",
        styles,
    ))
    story.append(make_table(
        ["表", "模型位置", "一句话"],
        [
            ["user_app", "accounts/models.py → UserApp", "身份、角色、停用"],
            ["category", "cms/models.py → Category", "文章栏目"],
            ["item", "cms/models.py → Item", "文章内容与发布状态"],
            ["comment", "cms/models.py → Comment", "评论内容与显隐状态"],
        ],
        [3 * cm, 5.5 * cm, 8 * cm], styles,
    ))

    story.append(h2("6.1 三个状态开关（代码里常判断）", styles))
    story.append(make_table(
        ["字段", "代码用途"],
        [
            ["user_type", "登录后跳转；管理端权限（普通/管理/超管）"],
            ["is_published", "前台 home 只取已发布文章"],
            ["is_hidden", "前台只展示 0；管理端 toggle 在 0/1 间切换"],
        ],
        [3.5 * cm, 13 * cm], styles,
    ))

    story.append(h1("第七章　一条主链路（代码走读）", styles))
    story.append(bullet("打开 /login/ → accounts.views.login_view 查 user_app；", styles))
    story.append(bullet("普通用户进 / → cms.views.home 查 item+category，再查可见 comment；", styles))
    story.append(bullet("发表评论 → comment_create 写 comment；", styles))
    story.append(bullet("管理员进 /manage/... → 各 list/form/toggle 视图维护栏目、文章、用户、评论显隐。", styles))

    story.append(Spacer(1, 8))
    story.append(h1("第八章　总结口诀", styles))
    story.append(body(
        "<b>config</b> 管配置与总路由；<b>accounts</b> 管人；<b>cms</b> 管内容与评论；"
        "<b>templates</b> 管长相；<b>static</b> 管样式；四张表把「人—栏目—文章—评论」串成完整 CMS。",
        styles,
    ))
    return story


if __name__ == "__main__":
    build_pdf(
        OUT,
        make_story,
        header_left="CMS 原型系统 · 代码实现逻辑的设计",
        header_right="Django MTV",
        title="代码实现逻辑的设计",
        author="CMS Homework",
    )
