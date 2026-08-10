# -*- coding: utf-8 -*-
"""数据库设计.pdf — 与项目说明书同一排版标准。"""
import math
from pathlib import Path

from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, Spacer, PageBreak, Flowable

from pdf_kit import (
    ACCENT, TITLE, TEXT, MUTED, LINE, SOFT, WHITE,
    build_pdf, cover_block, toc_block, h1, h2, body, bullet, make_table,
)

OUT = Path(__file__).resolve().parent / "数据库设计.pdf"


class ERDiagram(Flowable):
    def __init__(self, width=16.5 * cm, height=8.2 * cm):
        Flowable.__init__(self)
        self.box_width = width
        self.box_height = height

    def wrap(self, aw, ah):
        self.width = min(self.box_width, aw)
        self.height = self.box_height
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setStrokeColor(LINE)
        c.setFillColor(SOFT)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)

        def box(x, y, w, h, title, lines):
            c.setFillColor(WHITE)
            c.setStrokeColor(ACCENT)
            c.setLineWidth(1.35)
            c.roundRect(x, y, w, h, 5, fill=1, stroke=1)
            c.setFillColor(ACCENT)
            c.roundRect(x, y + h - 22, w, 22, 5, fill=1, stroke=0)
            c.rect(x, y + h - 22, w, 11, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("YaHeiBd", 10)
            c.drawCentredString(x + w / 2, y + h - 15, title)
            c.setFillColor(TEXT)
            c.setFont("YaHei", 8)
            ty = y + h - 36
            for line in lines:
                c.drawString(x + 8, ty, line)
                ty -= 12

        def arrow(x1, y1, x2, y2, label="", lab_x=None, lab_y=None):
            c.setStrokeColor(ACCENT)
            c.setFillColor(ACCENT)
            c.setLineWidth(1.15)
            c.line(x1, y1, x2, y2)
            ang = math.atan2(y2 - y1, x2 - x1)
            size = 7
            p1 = (x2 - size * math.cos(ang - 0.4), y2 - size * math.sin(ang - 0.4))
            p2 = (x2 - size * math.cos(ang + 0.4), y2 - size * math.sin(ang + 0.4))
            path = c.beginPath()
            path.moveTo(x2, y2)
            path.lineTo(*p1)
            path.lineTo(*p2)
            path.close()
            c.drawPath(path, fill=1, stroke=0)
            if label:
                c.setFillColor(MUTED)
                c.setFont("YaHei", 8)
                c.drawCentredString(
                    lab_x if lab_x is not None else (x1 + x2) / 2,
                    lab_y if lab_y is not None else (y1 + y2) / 2 + 4,
                    label,
                )

        box(18, 155, 150, 95, "category 栏目",
            ["PK  id", "    name (唯一)", "    description", "    created_at"])
        box(230, 145, 170, 110, "item 文章",
            ["PK  id", "FK  category_id", "    title / content", "    author (非外键)",
             "    published_at", "    is_published"])
        box(18, 20, 150, 105, "user_app 用户",
            ["PK  user_id", "    password / name", "    user_type",
             "    is_disabled", "    created_at / updated_at"])
        box(430, 70, 175, 120, "comment 评论",
            ["PK  id", "FK  user_id", "FK  item_id", "    content ≤100",
             "    user_name (冗余)", "    commented_at", "    is_hidden 0/1"])

        arrow(168, 200, 230, 200, "1 : N", 198, 208)
        arrow(315, 145, 430, 130, "1 : N", 370, 148)
        arrow(168, 70, 430, 110, "1 : N", 280, 78)

        c.setFillColor(MUTED)
        c.setFont("YaHei", 8)
        c.drawString(20, 8, "说明：箭头由父实体指向子实体；级联删除按外键策略执行。")


class SeqDiagram(Flowable):
    def __init__(self, actors, steps, width=16.5 * cm, height=None):
        Flowable.__init__(self)
        self.actors = actors
        self.steps = steps
        self.box_width = width
        n = len(steps)
        self.box_height = height or (2.2 * cm + n * 0.72 * cm)

    def wrap(self, aw, ah):
        self.width = min(self.box_width, aw)
        self.height = self.box_height
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setStrokeColor(LINE)
        c.setFillColor(SOFT)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)

        n = len(self.actors)
        margin_x = 40
        usable = self.width - 2 * margin_x
        gap = usable / max(n - 1, 1)
        xs = [margin_x + i * gap for i in range(n)]
        top = self.height - 28
        bottom = 18

        for i, name in enumerate(self.actors):
            bw, bh = 78, 22
            c.setFillColor(WHITE)
            c.setStrokeColor(ACCENT)
            c.setLineWidth(1.15)
            c.roundRect(xs[i] - bw / 2, top - bh / 2, bw, bh, 4, fill=1, stroke=1)
            c.setFillColor(TITLE)
            c.setFont("YaHeiBd", 8)
            c.drawCentredString(xs[i], top - 3, name)
            c.setStrokeColor(LINE)
            c.setDash(2, 2)
            c.setLineWidth(0.8)
            c.line(xs[i], top - bh / 2, xs[i], bottom)
            c.setDash()

        y = top - 38
        for fr, to, text, note in self.steps:
            x1, x2 = xs[fr], xs[to]
            c.setStrokeColor(ACCENT)
            c.setFillColor(ACCENT)
            c.setLineWidth(1.1)
            c.line(x1, y, x2, y)
            p = c.beginPath()
            if x2 >= x1:
                p.moveTo(x2, y)
                p.lineTo(x2 - 6, y + 3)
                p.lineTo(x2 - 6, y - 3)
            else:
                p.moveTo(x2, y)
                p.lineTo(x2 + 6, y + 3)
                p.lineTo(x2 + 6, y - 3)
            p.close()
            c.drawPath(p, fill=1, stroke=0)
            c.setFillColor(TEXT)
            c.setFont("YaHei", 7.5)
            mid = (x1 + x2) / 2
            c.drawCentredString(mid, y + 4, text)
            if note:
                c.setFillColor(MUTED)
                c.setFont("YaHei", 7)
                c.drawCentredString(mid, y - 10, note)
                y -= 26
            else:
                y -= 20


def make_story(styles):
    story = []
    story.extend(cover_block(
        styles,
        "数　据　库　设　计",
        "点击目录可跳转；侧边书签亦可导航。",
        [
            "数据库：MySQL（127.0.0.1:3307）",
            "库名：cms_prototype　　字符集：utf8mb4",
        ],
    ))
    story.append(PageBreak())
    story.extend(toc_block(styles))
    story.append(PageBreak())

    story.append(h1("第一章　设计概述", styles))
    story.append(body(
        "本系统是一个小型 CMS（内容管理系统）原型。业务可概括为："
        "<b>用户中枢 + 栏目组织文章 + 用户评论文章</b>。"
        "登录身份使用自定义表 user_app（非 Django 默认 auth_user）。"
        "文章按栏目归类，评论同时关联用户与文章。发布、停用、评论可见性通过状态字段控制。",
        styles,
    ))

    story.append(h2("1.1 技术环境", styles))
    story.append(make_table(
        ["项目", "说明"],
        [
            ["数据库引擎", "MySQL 8 / 9"],
            ["连接地址", "127.0.0.1:3307"],
            ["数据库名", "cms_prototype"],
            ["字符集", "utf8mb4"],
            ["访问方式", "Django ORM + 迁移"],
        ],
        [4.5 * cm, 12 * cm], styles,
    ))

    story.append(h2("1.2 核心业务表", styles))
    story.append(make_table(
        ["表名", "中文名", "作用"],
        [
            ["user_app", "用户表", "登录身份、角色类型、停用状态"],
            ["category", "栏目表", "文章分类"],
            ["item", "文章表", "正文、作者、发表时间与发布状态"],
            ["comment", "评论表", "用户评论及显示/隐藏状态"],
        ],
        [3.5 * cm, 3.2 * cm, 9.8 * cm], styles,
    ))

    story.append(h1("第二章　ER 实体关系图", styles))
    story.append(body(
        "下图给出四张核心表的实体联系。框内列出主键（PK）、外键（FK）与关键属性。"
        "关系基数均为 <b>1 : N</b>。",
        styles,
    ))
    story.append(Spacer(1, 4))
    story.append(ERDiagram())
    story.append(Paragraph("图 1　CMS 业务库 ER 图（带边框实体框）", styles["Caption"]))

    story.append(h2("2.1 关系与级联策略", styles))
    story.append(make_table(
        ["关系", "基数", "含义", "删除策略"],
        [
            ["category → item", "1 : N", "一篇文章必须属于一个栏目", "删栏目级联删文章"],
            ["item → comment", "1 : N", "一篇文章可有多条评论", "删文章级联删评论"],
            ["user_app → comment", "1 : N", "一个用户可发多条评论", "删用户级联删评论"],
        ],
        [4 * cm, 2 * cm, 6 * cm, 4.5 * cm], styles,
    ))
    story.append(body(
        "补充：item.author 为普通字符串（非外键）；comment.user_name 为发表时从用户姓名拷贝的冗余字段，便于按姓名查询。",
        styles,
    ))

    story.append(h1("第三章　表结构详细设计", styles))

    story.append(h2("3.1 user_app（用户表）", styles))
    story.append(make_table(
        ["字段", "类型/约束", "含义", "取值说明"],
        [
            ["user_id", "varchar(15), PK", "用户ID", "互斥主键"],
            ["password", "varchar(30)", "密码", "作业要求明文演示"],
            ["name", "varchar(30)", "用户姓名", "≤30 字符"],
            ["user_type", "smallint", "用户类型", "0管理员 / 1普通 / 2超管"],
            ["is_disabled", "smallint", "是否停用", "0正常 / 1停用"],
            ["created_at", "datetime", "创建时间", "自动写入"],
            ["updated_at", "datetime", "最近更新", "自动更新"],
        ],
        [3.2 * cm, 3.8 * cm, 3.2 * cm, 6.3 * cm], styles,
    ))

    story.append(h2("3.2 category（栏目表）", styles))
    story.append(make_table(
        ["字段", "类型/约束", "含义", "取值说明"],
        [
            ["id", "整型自增, PK", "栏目ID", "主键"],
            ["name", "varchar(100), 唯一", "栏目名称", "如通知公告等"],
            ["description", "varchar(255)", "简介", "可空"],
            ["created_at", "datetime", "创建时间", "自动写入"],
        ],
        [3.2 * cm, 4.2 * cm, 3.2 * cm, 5.9 * cm], styles,
    ))

    story.append(h2("3.3 item（文章表）", styles))
    story.append(make_table(
        ["字段", "类型/约束", "含义", "取值说明"],
        [
            ["id", "整型自增, PK", "文章ID", "主键"],
            ["title", "varchar(200)", "标题", ""],
            ["content", "text", "正文", ""],
            ["category_id", "FK → category.id", "所属栏目", "必填外键"],
            ["author", "varchar(30)", "作者", "字符串，非外键"],
            ["published_at", "datetime", "发表时间", "支持区间查询"],
            ["is_published", "bool", "是否发布", "前台只看已发布"],
            ["created_at / updated_at", "datetime", "时间戳", "自动维护"],
        ],
        [3.8 * cm, 4 * cm, 3 * cm, 5.7 * cm], styles,
    ))

    story.append(h2("3.4 comment（评论表）", styles))
    story.append(make_table(
        ["字段", "类型/约束", "含义", "取值说明"],
        [
            ["id", "整型自增, PK", "评论ID", "主键"],
            ["user_id", "FK → user_app.user_id", "评论用户", "外键"],
            ["item_id", "FK → item.id", "评论文章", "外键"],
            ["content", "varchar(100)", "评论内容", "不超过100字"],
            ["user_name", "varchar(30)", "用户姓名", "发表时冗余拷贝"],
            ["commented_at", "datetime", "评论时间", "自动写入"],
            ["is_hidden", "smallint", "是否显示", "0显示 / 1删除隐藏"],
            ["updated_at", "datetime", "更新时间", "显隐切换时更新"],
        ],
        [3.2 * cm, 4.5 * cm, 3 * cm, 5.8 * cm], styles,
    ))

    story.append(PageBreak())
    story.append(h1("第四章　状态字段与业务开关", styles))
    story.append(body("系统通过三组状态字段控制账号可用性、文章发布与评论可见性：", styles, indent=False))
    story.append(make_table(
        ["字段", "所在表", "取值", "业务效果"],
        [
            ["is_disabled", "user_app", "0正常 / 1停用", "停用账号无法登录"],
            ["is_published", "item", "True / False", "前台仅展示已发布文章"],
            ["is_hidden", "comment", "0显示 / 1隐藏", "前台只展示可见评论"],
        ],
        [3.5 * cm, 3.2 * cm, 4.3 * cm, 5.5 * cm], styles,
    ))

    story.append(h1("第五章　角色与数据权限", styles))
    story.append(make_table(
        ["角色", "user_type", "主要数据权限"],
        [
            ["普通用户", "1", "读已发布文章；写评论；前台多条件查询"],
            ["管理员", "0", "栏目/文章 CRUD；管理普通用户；评论显隐"],
            ["超级用户", "2", "具备管理员能力，并可管理管理员账号"],
        ],
        [3.2 * cm, 2.8 * cm, 10.5 * cm], styles,
    ))

    story.append(h1("第六章　关键业务时序图", styles))
    story.append(body(
        "下列时序图描述应用与数据库的交互。角色框、生命线与消息箭头均带边框/描边，便于阅读。",
        styles,
    ))

    story.append(h2("6.1 用户登录分流", styles))
    story.append(SeqDiagram(
        ["浏览器", "Django视图", "user_app"],
        [
            (0, 1, "POST user_id + password", None),
            (1, 2, "SELECT 按 user_id 查询", None),
            (2, 1, "返回用户记录", None),
            (1, 1, "校验密码 / is_disabled / user_type", "失败则返回错误提示"),
            (1, 0, "写 session 并按角色跳转", "1→前台；0/2→管理台"),
        ],
        height=6.2 * cm,
    ))
    story.append(Paragraph("图 2　登录时序图", styles["Caption"]))
    story.append(body("说明：登录过程只读 user_app，不写其他业务表。", styles))

    story.append(h2("6.2 前台浏览文章并发表评论", styles))
    story.append(SeqDiagram(
        ["普通用户", "Django", "item/category", "comment"],
        [
            (0, 1, "打开前台 / 条件查询", None),
            (1, 2, "查已发布文章(+栏目)", "is_published = 1"),
            (2, 1, "返回文章列表", None),
            (1, 3, "查该文可见评论", "is_hidden = 0"),
            (3, 1, "返回评论列表", None),
            (1, 0, "渲染左列表+右正文/评论", None),
            (0, 1, "POST 发表评论", None),
            (1, 2, "校验文章已发布", None),
            (1, 3, "INSERT comment", "写入 user_name, is_hidden=0"),
            (1, 0, "回到该文并刷新评论", None),
        ],
        height=9.2 * cm,
    ))
    story.append(Paragraph("图 3　浏览与发评时序图", styles["Caption"]))

    story.append(h2("6.3 管理员切换评论可见性", styles))
    story.append(SeqDiagram(
        ["管理员", "Django", "comment"],
        [
            (0, 1, "打开评论管理/按内容或姓名查询", None),
            (1, 2, "SELECT 评论列表", "可模糊匹配"),
            (2, 1, "返回结果集", None),
            (0, 1, "切换显示 / 不显示", None),
            (1, 2, "UPDATE is_hidden 0/1", "前台随即不可见或可见"),
        ],
        height=5.8 * cm,
    ))
    story.append(Paragraph("图 4　评论显隐管理时序图", styles["Caption"]))

    story.append(h2("6.4 管理员维护文章（简述）", styles))
    story.append(bullet("在文章管理中查询 item（可按标题、作者、发表时间）；", styles))
    story.append(bullet("新增/编辑时选择 category_id，写入标题、正文、作者、时间与发布状态；", styles))
    story.append(bullet("删除文章时，因外键级联，对应 comment 一并删除。", styles))

    story.append(h1("第七章　典型查询与库表对应", styles))
    story.append(make_table(
        ["功能", "主要涉及表", "关键条件示例"],
        [
            ["按栏目浏览", "item, category", "category_id=? AND is_published=1"],
            ["按标题模糊查", "item", "title LIKE %关键词%"],
            ["按作者模糊查", "item", "author LIKE %关键词%"],
            ["按时间范围查", "item", "published_at BETWEEN 起 AND 止"],
            ["前台看评论", "comment", "item_id=? AND is_hidden=0"],
            ["管理端评审查询", "comment", "content / user_name 模糊匹配"],
            ["用户登录", "user_app", "user_id=? 且校验 password、is_disabled"],
        ],
        [3.5 * cm, 4 * cm, 9 * cm], styles,
    ))

    story.append(h1("第八章　设计总结", styles))
    story.append(body(
        "本数据库以「栏目—文章—评论」为主线，以「用户」为身份中枢："
        "category 负责内容分类；item 承载可发布内容并通过 is_published 控制前台可见；"
        "user_app 统一登录与权限类型；comment 连接用户与文章，并通过 is_hidden 实现软删除式可见性控制。"
        "整体结构清晰，满足 CMS 原型的增删改查、多条件检索与评论管理需求。",
        styles,
    ))
    return story


if __name__ == "__main__":
    build_pdf(
        OUT,
        make_story,
        header_left="CMS 原型系统 · 数据库设计",
        header_right="MySQL / cms_prototype",
        title="CMS原型系统数据库设计",
        author="CMS Homework",
    )
