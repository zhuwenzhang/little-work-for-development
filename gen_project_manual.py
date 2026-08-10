# -*- coding: utf-8 -*-
"""CMS 项目说明书 — 可点击目录 + 中文排版细节"""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable,
    KeepTogether, HRFlowable,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

OUT = Path(__file__).resolve().parent / "项目说明书.pdf"
pdfmetrics.registerFont(TTFont("YaHei", r"C:\Windows\Fonts\msyh.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("YaHeiBd", r"C:\Windows\Fonts\msyhbd.ttc", subfontIndex=0))

ACCENT = colors.HexColor("#1F6F5B")
TITLE = colors.HexColor("#1B2420")
TEXT = colors.HexColor("#2C3A33")
MUTED = colors.HexColor("#5F6F67")
LINE = colors.HexColor("#D0DBD5")
BG = colors.HexColor("#F5F8F6")
SOFT = colors.HexColor("#EEF5F1")
WHITE = colors.white

# 中文正文：字号 10.5，行距约 1.65 倍；首行缩进约 2 字
BODY_SIZE = 10.5
BODY_LEADING = 17.5
INDENT_2CHARS = BODY_SIZE * 2


def build_styles():
    ss = getSampleStyleSheet()
    common = dict(fontName="YaHei", wordWrap="CJK", splitLongWords=1)

    ss.add(ParagraphStyle(
        "CoverTitle", fontName="YaHeiBd", fontSize=26, leading=38,
        alignment=TA_CENTER, textColor=TITLE, spaceAfter=8,
        wordWrap="CJK",
    ))
    ss.add(ParagraphStyle(
        "CoverSub", **common, fontSize=11.5, leading=19,
        alignment=TA_CENTER, textColor=MUTED, spaceBefore=2, spaceAfter=4,
    ))
    ss.add(ParagraphStyle(
        "H1", fontName="YaHeiBd", fontSize=15.5, leading=24,
        textColor=ACCENT, spaceBefore=4, spaceAfter=12,
        wordWrap="CJK", borderPadding=(0, 0, 4, 0),
    ))
    ss.add(ParagraphStyle(
        "H2", fontName="YaHeiBd", fontSize=12, leading=19,
        textColor=TITLE, spaceBefore=14, spaceAfter=8,
        wordWrap="CJK",
    ))
    ss.add(ParagraphStyle(
        "Body", **common, fontSize=BODY_SIZE, leading=BODY_LEADING,
        textColor=TEXT, alignment=TA_JUSTIFY,
        firstLineIndent=INDENT_2CHARS,
        spaceBefore=0, spaceAfter=9,
    ))
    ss.add(ParagraphStyle(
        "BodyFlush", **common, fontSize=BODY_SIZE, leading=BODY_LEADING,
        textColor=TEXT, alignment=TA_JUSTIFY,
        firstLineIndent=0, spaceBefore=0, spaceAfter=8,
    ))
    ss.add(ParagraphStyle(
        "BulletItem", **common, fontSize=BODY_SIZE, leading=BODY_LEADING,
        textColor=TEXT, leftIndent=22, firstLineIndent=-12,
        spaceBefore=1.5, spaceAfter=4.5,
    ))
    ss.add(ParagraphStyle(
        "Caption", **common, fontSize=9, leading=13,
        textColor=MUTED, alignment=TA_CENTER,
        spaceBefore=8, spaceAfter=14,
    ))
    ss.add(ParagraphStyle(
        "Cell", **common, fontSize=9, leading=13.5, textColor=TEXT,
    ))
    ss.add(ParagraphStyle(
        "CellHead", fontName="YaHeiBd", fontSize=9, leading=13.5,
        textColor=WHITE, alignment=TA_CENTER, wordWrap="CJK",
    ))
    ss.add(ParagraphStyle(
        "TocTitle", fontName="YaHeiBd", fontSize=18, leading=28,
        textColor=ACCENT, alignment=TA_CENTER, spaceAfter=6,
        wordWrap="CJK",
    ))
    # 目录：悬挂缩进 + 点线引导（TableOfContents 自带 dots）
    ss.add(ParagraphStyle(
        "TOC1", fontName="YaHeiBd", fontSize=11, leading=20,
        leftIndent=14, firstLineIndent=-14,
        spaceBefore=9, spaceAfter=3,
        textColor=TITLE, wordWrap="CJK",
    ))
    ss.add(ParagraphStyle(
        "TOC2", **common, fontSize=10, leading=17,
        leftIndent=28, firstLineIndent=-12,
        spaceBefore=2, spaceAfter=2,
        textColor=TEXT,
    ))
    return ss


def draw_page(canvas, doc):
    """页眉页脚。不用 NumberedCanvas，避免破坏 bookmark / 目录跳转。"""
    canvas.saveState()
    w, h = A4
    # 封面不画页码栏（第 1 页）
    if doc.page == 1:
        canvas.restoreState()
        return

    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.7)
    canvas.line(2 * cm, h - 1.35 * cm, w - 2 * cm, h - 1.35 * cm)
    canvas.setFont("YaHei", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, h - 1.1 * cm, "CMS 原型系统 · 项目说明书")
    canvas.drawRightString(w - 2 * cm, h - 1.1 * cm, "Django + MySQL")

    canvas.line(2 * cm, 1.4 * cm, w - 2 * cm, 1.4 * cm)
    total = getattr(doc, "page_count", None) or doc.page
    # 目录页起从「第 2 页」起算文档页码时，仍用 PDF 物理页码更直观
    canvas.drawCentredString(w / 2, 0.9 * cm, f"第 {doc.page} 页 / 共 {total} 页")
    canvas.restoreState()


class MyDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        BaseDocTemplate.__init__(self, filename, **kwargs)
        frame = Frame(
            self.leftMargin, self.bottomMargin,
            self.width, self.height,
            id="normal", showBoundary=0,
            leftPadding=0, rightPadding=0, topPadding=2, bottomPadding=2,
        )
        self.addPageTemplates([
            PageTemplate(id="main", frames=frame, onPage=draw_page),
        ])
        self.page_count = None

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        style = flowable.style.name
        text = flowable.getPlainText().strip()
        if style == "H1":
            key = f"h1-{self.seq.nextf('h1')}"
            # FitH 定位到标题附近，阅读器跳转更稳
            self.canv.bookmarkPage(key, fit="FitH", top=self.canv._pagesize[1] - 2.2 * cm)
            self.canv.addOutlineEntry(text, key, level=0, closed=0)
            self.notify("TOCEntry", (0, text, self.page, key))
        elif style == "H2":
            key = f"h2-{self.seq.nextf('h2')}"
            self.canv.bookmarkPage(key, fit="FitH", top=self.canv._pagesize[1] - 2.2 * cm)
            self.canv.addOutlineEntry(text, key, level=1, closed=0)
            self.notify("TOCEntry", (1, text, self.page, key))


class InfoBox(Flowable):
    def __init__(self, title, lines, width=16.5 * cm):
        Flowable.__init__(self)
        self.title = title
        self.lines = lines
        self.box_width = width
        self._h = 0.95 * cm + len(lines) * 0.5 * cm

    def wrap(self, aw, ah):
        self.width = min(self.box_width, aw)
        self.height = self._h
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(SOFT)
        c.setStrokeColor(ACCENT)
        c.setLineWidth(1.1)
        c.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=1)
        c.setFillColor(ACCENT)
        c.roundRect(0, self.height - 0.62 * cm, self.width, 0.62 * cm, 4, fill=1, stroke=0)
        c.rect(0, self.height - 0.62 * cm, self.width, 0.31 * cm, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("YaHeiBd", 9)
        c.drawString(10, self.height - 0.42 * cm, self.title)
        c.setFillColor(TEXT)
        c.setFont("YaHei", 9)
        y = self.height - 1.02 * cm
        for line in self.lines:
            c.drawString(12, y, line)
            y -= 0.48 * cm


class ArchDiagram(Flowable):
    def __init__(self, width=16.5 * cm, height=5.4 * cm):
        Flowable.__init__(self)
        self.box_width = width
        self.box_height = height

    def wrap(self, aw, ah):
        self.width = min(self.box_width, aw)
        self.height = self.box_height
        return self.width, self.height

    def _box(self, c, x, y, w, h, title, sub):
        c.setFillColor(WHITE)
        c.setStrokeColor(ACCENT)
        c.setLineWidth(1.15)
        c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
        c.setFillColor(ACCENT)
        c.setFont("YaHeiBd", 9)
        c.drawCentredString(x + w / 2, y + h - 15, title)
        c.setFillColor(TEXT)
        c.setFont("YaHei", 8)
        c.drawCentredString(x + w / 2, y + 10, sub)

    def draw(self):
        c = self.canv
        c.setFillColor(SOFT)
        c.setStrokeColor(LINE)
        c.setLineWidth(0.9)
        c.roundRect(0, 0, self.width, self.height, 5, fill=1, stroke=1)
        cx = self.width / 2
        self._box(c, cx - 60, 118, 120, 40, "浏览器", "用户请求")
        c.setStrokeColor(ACCENT)
        c.setLineWidth(1.1)
        c.line(cx, 118, cx, 100)
        p = c.beginPath()
        p.moveTo(cx, 95)
        p.lineTo(cx - 4, 102)
        p.lineTo(cx + 4, 102)
        p.close()
        c.setFillColor(ACCENT)
        c.drawPath(p, fill=1, stroke=0)
        self._box(c, cx - 90, 62, 180, 36, "config / urls", "总路由分发")
        c.line(cx - 45, 62, cx - 135, 48)
        c.line(cx + 45, 62, cx + 125, 48)
        self._box(c, 25, 8, 155, 38, "accounts", "登录 · 注册 · 鉴权")
        self._box(c, self.width - 200, 8, 175, 38, "cms", "栏目 · 文章 · 评论")


def make_table(headers, rows, widths, styles):
    data = [[Paragraph(h, styles["CellHead"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(x), styles["Cell"]) for x in row])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, BG]),
        ("GRID", (0, 0), (-1, -1), 0.55, LINE),
        ("BOX", (0, 0), (-1, -1), 1.1, ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def h1(text, styles):
    return KeepTogether([
        Paragraph(text, styles["H1"]),
        HRFlowable(width="100%", thickness=0.9, color=ACCENT,
                   spaceBefore=0, spaceAfter=10, hAlign="LEFT"),
    ])


def h2(text, styles):
    return Paragraph(text, styles["H2"])


def body(text, styles, indent=True):
    return Paragraph(text, styles["Body"] if indent else styles["BodyFlush"])


def bullet(text, styles):
    return Paragraph(f"•  {text}", styles["BulletItem"])


def make_story(styles):
    story = []

    # ===== Cover =====
    story.append(Spacer(1, 2.4 * cm))
    story.append(Paragraph("CMS 原型系统", styles["CoverTitle"]))
    story.append(Spacer(1, 0.2 * cm))
    story.append(HRFlowable(
        width="55%", thickness=1.3, color=ACCENT,
        spaceBefore=6, spaceAfter=12, hAlign="CENTER",
    ))
    story.append(Paragraph("项　目　说　明　书", styles["CoverTitle"]))
    story.append(Spacer(1, 0.45 * cm))
    story.append(Paragraph("Python · Django · MySQL（端口 3307）", styles["CoverSub"]))
    story.append(Paragraph("库名：cms_prototype　　字符集：utf8mb4", styles["CoverSub"]))
    story.append(Spacer(1, 0.9 * cm))
    story.append(InfoBox("文档资料来源", [
        "数据库设计.txt / 数据库设计.pdf",
        "界面设计及实现逻辑.txt　·　代码实现逻辑的设计.txt / .pdf",
        "修改日志.txt　·　并结合当前工程代码整理",
    ]))
    story.append(Spacer(1, 0.7 * cm))
    story.append(Paragraph(
        "请使用 PDF 阅读器打开：点击「目录」条目可跳转；侧边「书签」面板亦可导航。",
        styles["Caption"],
    ))
    story.append(PageBreak())

    # ===== TOC =====
    story.append(Paragraph("目　录", styles["TocTitle"]))
    story.append(HRFlowable(
        width="100%", thickness=0.8, color=LINE,
        spaceBefore=2, spaceAfter=14,
    ))
    toc = TableOfContents()
    toc.levelStyles = [styles["TOC1"], styles["TOC2"]]
    toc.dotsMinLevel = 0
    # 点线与页码间距更易读
    toc.tableStyle = TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ])
    story.append(toc)
    story.append(PageBreak())

    # ===== Ch1 =====
    story.append(h1("第一章　项目概述", styles))
    story.append(body(
        "本系统是一个基于 <b>Python + Django + MySQL</b> 的 CMS（内容管理）原型，用于完成课程作业要求："
        "至少包含栏目（Category）与文章（Item）；管理员可对栏目、文章增删改查并发布；"
        "普通用户可浏览已发布内容并按条件查询。项目后续扩展了评论（Comment）、用户管理、左右分栏界面等能力。",
        styles,
    ))
    story.append(body("系统角色分为三类：", styles, indent=False))
    story.append(bullet("<b>普通用户</b>（user_type=1）：注册、登录、浏览、查询、发表评论。", styles))
    story.append(bullet("<b>管理员</b>（user_type=0）：栏目 / 文章 / 普通用户 / 评论管理。", styles))
    story.append(bullet("<b>超级用户</b>（user_type=2）：具备管理员能力，并可管理管理员账号。", styles))
    story.append(Spacer(1, 8))
    story.append(ArchDiagram())
    story.append(Paragraph("图 1　系统请求分发示意", styles["Caption"]))

    # ===== Ch2 =====
    story.append(h1("第二章　运行环境与快速使用", styles))
    story.append(h2("2.1 环境要求", styles))
    story.append(make_table(
        ["项目", "说明"],
        [
            ["操作系统", "Windows 10 / 11"],
            ["Python", "建议 3.10+（venv / Anaconda）"],
            ["依赖", "requirements.txt：Django、PyMySQL、cryptography"],
            ["MySQL", "本机 MySQL 9.x；作业实例独立监听 <b>3307</b>（不占用 3306）"],
            ["IDE", "VS Code / Cursor，打开桌面「小作业」目录"],
        ],
        [3.6 * cm, 12.9 * cm], styles,
    ))

    story.append(h2("2.2 一键启动与停止", styles))
    story.append(body("在项目根目录终端执行：", styles, indent=False))
    story.append(InfoBox("启动　.\\start.bat　或　.\\start.ps1", [
        "① 启动 MySQL 3307　　② 准备库 cms_prototype",
        "③ 执行 migrate　　④ 启动 Django（http://127.0.0.1:8000）",
        "数据目录：%LOCALAPPDATA%\\cms_prototype_mysql\\（英文路径）",
    ]))
    story.append(Spacer(1, 10))
    story.append(InfoBox("停止　.\\stop.bat　或　.\\stop.ps1", [
        "停止 Django（8000）与作业用 MySQL 3307",
        "不影响系统服务 MySQL91 / 端口 3306",
    ]))

    story.append(h2("2.3 访问地址与测试账号", styles))
    story.append(make_table(
        ["页面", "地址"],
        [
            ["登录页", "http://127.0.0.1:8000/login/"],
            ["注册页", "http://127.0.0.1:8000/register/"],
            ["前台（登录后）", "http://127.0.0.1:8000/"],
            ["管理台（登录后）", "http://127.0.0.1:8000/manage/"],
        ],
        [4.2 * cm, 12.3 * cm], styles,
    ))
    story.append(Spacer(1, 8))
    story.append(body(
        "登录后按数据库中的 <b>user_type</b> 自动跳转（无需在登录页选择身份）：",
        styles, indent=False,
    ))
    story.append(make_table(
        ["用户ID", "密码", "类型", "说明"],
        [
            ["super", "1", "超级用户 (2)", "可管普通用户与管理员"],
            ["admin", "1", "管理员 (0)", "可管普通用户"],
            ["user01", "1", "普通用户 (1)", "前台浏览 / 查询 / 评论"],
            ["liyidong 等", "123456", "普通用户", "教师拼音账号（导入数据）"],
        ],
        [3.4 * cm, 2.4 * cm, 3.6 * cm, 7.1 * cm], styles,
    ))
    story.append(body(
        "数据库连接（config/settings.py）：Host=<b>127.0.0.1</b>，Port=<b>3307</b>，"
        "Database=<b>cms_prototype</b>，User=root，Password=123456。",
        styles,
    ))

    story.append(h2("2.4 普通用户怎么用", styles))
    story.append(bullet("打开注册页，填写用户 ID、密码、姓名（只能注册普通用户；ID 冲突会弹窗提示）。", styles))
    story.append(bullet("注册成功约 <b>0.5 秒</b>后跳转登录；登录成功进入前台文章浏览。", styles))
    story.append(bullet("顶部分栏切换栏目；左侧点标题，右侧查看全文。", styles))
    story.append(bullet("查询模式：按题目 / 发表时间 / 作者（模糊匹配）。", styles))
    story.append(bullet("正文下方可发表评论（不超过 100 字），并查看可见评论（is_hidden=0）。", styles))

    story.append(h2("2.5 管理员怎么用", styles))
    story.append(bullet("使用 admin 或 super 登录，进入左侧导航管理台。", styles))
    story.append(bullet("<b>栏目管理</b>：新增 / 编辑 / 删除栏目。", styles))
    story.append(bullet("<b>文章管理</b>：发布文章；按题 / 时 / 作者查询后编辑或删除。", styles))
    story.append(bullet("<b>用户管理</b>：新增用户；按 ID / 姓名查询；停用或初始化密码为 123456。", styles))
    story.append(bullet("管理员只能管普通用户；超级用户还可管管理员账号。", styles))
    story.append(bullet("<b>评论管理</b>：按内容 / 姓名查询；切换评论显示或隐藏。", styles))

    story.append(PageBreak())

    # ===== Ch3 =====
    story.append(h1("第三章　需求分析与功能对照", styles))
    story.append(body(
        "依据《界面设计及实现逻辑.txt》及后续扩展，实现对照如下：",
        styles,
    ))
    story.append(make_table(
        ["需求点", "实现情况"],
        [
            ["注册（普通用户，ID 冲突提示，成功后跳转登录）", "已实现（跳转约 0.5 秒）"],
            ["登录校验；按库中 user_type 自动进前台 / 管理台", "已实现（取消登录页身份下拉）"],
            ["前台：已发布文章列表 / 详情", "已实现（左列表右详情）"],
            ["查询：题目 / 时间 / 栏目", "已实现；另增「按作者」"],
            ["管理端：栏目、文章增删改查", "已实现"],
            ["用户管理：按角色增加与停用", "已实现；并支持初始化密码"],
            ["评论：前台发表与展示；管理端显隐", "已实现（扩展）"],
        ],
        [8.6 * cm, 7.9 * cm], styles,
    ))

    # ===== Ch4 =====
    story.append(h1("第四章　数据库设计摘要", styles))
    story.append(body(
        "详细 ER 图与时序图见同目录《数据库设计.pdf》。此处摘要核心业务表（端口 3307，库 cms_prototype）：",
        styles,
    ))
    story.append(make_table(
        ["表名", "要点"],
        [
            ["user_app", "PK=user_id（≤15）；password 明文演示；user_type 0/1/2；is_disabled 0/1；name≤30"],
            ["category", "栏目名称、简介、创建时间"],
            ["item", "标题 / 正文 / 作者 / 发表时间 / 是否发布；外键 → category"],
            ["comment", "外键 → user_id、item_id；content≤100；user_name 冗余；is_hidden：0 显示 / 1 隐藏"],
        ],
        [3.4 * cm, 13.1 * cm], styles,
    ))
    story.append(body(
        "关系主线：<b>category 1—N item 1—N comment N—1 user_app</b>。"
        "三个状态开关：is_disabled（账号）、is_published（文章）、is_hidden（评论）。",
        styles,
    ))
    story.append(body(
        "样例数据：约 100 篇整理自 cs.bjtu.edu.cn 的文章（5 个栏目，发表时间 2026-01～2026-07）；"
        "约 20 个教师拼音普通账号，每篇文章 3～5 条可见评论。",
        styles,
    ))

    # ===== Ch5 =====
    story.append(h1("第五章　代码结构与实现逻辑", styles))
    story.append(body(
        "详细说明见《代码实现逻辑的设计.pdf》。目录职责摘要如下：",
        styles,
    ))
    story.append(make_table(
        ["目录", "含义"],
        [
            ["config/", "settings、总 urls、PyMySQL 接入"],
            ["accounts/", "用户模型、登录注册、session 鉴权"],
            ["cms/", "栏目 / 文章 / 评论业务与管理视图"],
            ["templates/", "HTML 页面模板"],
            ["static/", "CSS 等静态资源"],
        ],
        [3.5 * cm, 13 * cm], styles,
    ))
    story.append(body(
        "约定：<b>models.py</b> 对应表结构；<b>views.py</b> 对应功能；<b>urls.py</b> 对应路径映射。"
        "请求链：浏览器 → config/urls → accounts | cms 的 urls → views → models → templates。",
        styles,
    ))

    # ===== Ch6 =====
    story.append(h1("第六章　界面与模块映射", styles))
    story.append(make_table(
        ["界面", "主要文件", "功能"],
        [
            ["登录 / 注册", "accounts/views.py<br/>templates/accounts/*.html", "注册、登录分流、退出"],
            ["前台浏览", "cms/views.home<br/>templates/cms/home.html", "分栏 + 查询 + 评论"],
            ["管理壳", "templates/cms/admin_base.html", "左侧导航 + 右侧内容"],
            ["栏目 / 文章 / 用户 / 评论", "cms/views 各模块<br/>templates/cms/*", "后台 CRUD 与评论显隐"],
        ],
        [3.4 * cm, 6.2 * cm, 6.9 * cm], styles,
    ))

    # ===== Ch7 =====
    story.append(h1("第七章　变更与扩展记录", styles))
    story.append(body("摘自《修改日志.txt》的要点：", styles))
    logs = [
        "修复 start.ps1 编码与 MySQL 密码连接顺序；新增 stop.bat。",
        "用户管理隐藏密码列，增加「初始化密码 = 123456」。",
        "注册 / 登录自动跳转改为约 0.5 秒；登录取消身份下拉，按库类型跳转。",
        "前台增加按作者查询；左右分栏浏览；管理端侧栏布局与按钮描边。",
        "导入约 100 篇文章、5 栏目；文章 / 用户管理增加查询框。",
        "扩展评论功能；导入教师账号与批量评论；去掉登录页演示账号提示。",
    ]
    for i, line in enumerate(logs, 1):
        story.append(bullet(f"{i}. {line}", styles))

    # ===== Ch8 =====
    story.append(h1("第八章　总结", styles))
    story.append(body(
        "本项目完成了一个可运行的 Django CMS 原型：账号分层、栏目文章管理、前台检索浏览、评论发表与审核，"
        "并通过独立 MySQL 3307 实例避免与本机 3306 冲突。日常使用优先通过 start.bat / stop.bat 管理生命周期；"
        "深入设计请参阅同目录《数据库设计.pdf》与《代码实现逻辑的设计.pdf》。",
        styles,
    ))
    story.append(Spacer(1, 12))
    story.append(InfoBox("附录　相关文件一览", [
        "数据库设计.txt / 数据库设计.pdf　—　表结构、ER、时序",
        "界面设计及实现逻辑.txt　—　页面与角色需求",
        "代码实现逻辑的设计.txt / .pdf　—　目录与界面代码映射",
        "修改日志.txt　—　迭代记录　　README.md / start·stop　—　运行启停",
    ]))
    return story


def _doc(path, page_count=None):
    doc = MyDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=2.15 * cm,
        rightMargin=2.15 * cm,
        topMargin=2.15 * cm,
        bottomMargin=2.05 * cm,
        title="CMS原型系统项目说明书",
        author="CMS Homework",
    )
    doc.page_count = page_count
    return doc


def build():
    styles = build_styles()
    # 第一遍：算出总页数（flowable 只能用一次，故每次重建 story）
    tmp = OUT.with_suffix(".tmp.pdf")
    doc1 = _doc(tmp)
    doc1.multiBuild(make_story(styles))
    total = doc1.page

    # 第二遍：写入终稿，页脚显示「第 x / 共 y」
    doc2 = _doc(OUT, page_count=total)
    doc2.multiBuild(make_story(styles))
    if tmp.exists():
        tmp.unlink(missing_ok=True)

    print("SAVED", OUT)
    print("PAGES", total, "SIZE", OUT.stat().st_size)


if __name__ == "__main__":
    build()
