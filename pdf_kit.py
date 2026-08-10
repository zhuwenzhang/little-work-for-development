# -*- coding: utf-8 -*-
"""共享 PDF 排版工具：可点击目录、中文 CJK、页眉页脚（不破坏书签）。"""
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Table, TableStyle, KeepTogether, HRFlowable,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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

BODY_SIZE = 10.5
BODY_LEADING = 17.5
INDENT_2CHARS = BODY_SIZE * 2


def build_styles():
    ss = getSampleStyleSheet()
    common = dict(fontName="YaHei", wordWrap="CJK", splitLongWords=1)

    ss.add(ParagraphStyle(
        "CoverTitle", fontName="YaHeiBd", fontSize=26, leading=38,
        alignment=TA_CENTER, textColor=TITLE, spaceAfter=8, wordWrap="CJK",
    ))
    ss.add(ParagraphStyle(
        "CoverSub", **common, fontSize=11.5, leading=19,
        alignment=TA_CENTER, textColor=MUTED, spaceBefore=2, spaceAfter=4,
    ))
    ss.add(ParagraphStyle(
        "H1", fontName="YaHeiBd", fontSize=15.5, leading=24,
        textColor=ACCENT, spaceBefore=4, spaceAfter=12, wordWrap="CJK",
    ))
    ss.add(ParagraphStyle(
        "H2", fontName="YaHeiBd", fontSize=12, leading=19,
        textColor=TITLE, spaceBefore=14, spaceAfter=8, wordWrap="CJK",
    ))
    ss.add(ParagraphStyle(
        "Body", **common, fontSize=BODY_SIZE, leading=BODY_LEADING,
        textColor=TEXT, alignment=TA_JUSTIFY,
        firstLineIndent=INDENT_2CHARS, spaceBefore=0, spaceAfter=9,
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
        textColor=MUTED, alignment=TA_CENTER, spaceBefore=8, spaceAfter=14,
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
        textColor=ACCENT, alignment=TA_CENTER, spaceAfter=6, wordWrap="CJK",
    ))
    ss.add(ParagraphStyle(
        "TOC1", fontName="YaHeiBd", fontSize=11, leading=20,
        leftIndent=14, firstLineIndent=-14,
        spaceBefore=9, spaceAfter=3, textColor=TITLE, wordWrap="CJK",
    ))
    ss.add(ParagraphStyle(
        "TOC2", **common, fontSize=10, leading=17,
        leftIndent=28, firstLineIndent=-12,
        spaceBefore=2, spaceAfter=2, textColor=TEXT,
    ))
    return ss


def draw_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    if doc.page == 1:
        canvas.restoreState()
        return
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.7)
    canvas.line(2 * cm, h - 1.35 * cm, w - 2 * cm, h - 1.35 * cm)
    canvas.setFont("YaHei", 8)
    canvas.setFillColor(MUTED)
    left = getattr(doc, "header_left", "CMS 原型系统")
    right = getattr(doc, "header_right", "Django + MySQL")
    canvas.drawString(2 * cm, h - 1.1 * cm, left)
    canvas.drawRightString(w - 2 * cm, h - 1.1 * cm, right)
    canvas.line(2 * cm, 1.4 * cm, w - 2 * cm, 1.4 * cm)
    total = getattr(doc, "page_count", None) or doc.page
    canvas.drawCentredString(w / 2, 0.9 * cm, f"第 {doc.page} 页 / 共 {total} 页")
    canvas.restoreState()


class DocTemplate(BaseDocTemplate):
    def __init__(self, filename, header_left="", header_right="", **kwargs):
        BaseDocTemplate.__init__(self, filename, **kwargs)
        self.header_left = header_left
        self.header_right = header_right
        self.page_count = None
        frame = Frame(
            self.leftMargin, self.bottomMargin,
            self.width, self.height,
            id="normal", showBoundary=0,
            leftPadding=0, rightPadding=0, topPadding=2, bottomPadding=2,
        )
        self.addPageTemplates([
            PageTemplate(id="main", frames=frame, onPage=draw_page),
        ])

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        style = flowable.style.name
        text = flowable.getPlainText().strip()
        top = self.canv._pagesize[1] - 2.2 * cm
        if style == "H1":
            key = f"h1-{self.seq.nextf('h1')}"
            self.canv.bookmarkPage(key, fit="FitH", top=top)
            self.canv.addOutlineEntry(text, key, level=0, closed=0)
            self.notify("TOCEntry", (0, text, self.page, key))
        elif style == "H2":
            key = f"h2-{self.seq.nextf('h2')}"
            self.canv.bookmarkPage(key, fit="FitH", top=top)
            self.canv.addOutlineEntry(text, key, level=1, closed=0)
            self.notify("TOCEntry", (1, text, self.page, key))


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
        HRFlowable(
            width="100%", thickness=0.9, color=ACCENT,
            spaceBefore=0, spaceAfter=10, hAlign="LEFT",
        ),
    ])


def h2(text, styles):
    return Paragraph(text, styles["H2"])


def body(text, styles, indent=True):
    return Paragraph(text, styles["Body"] if indent else styles["BodyFlush"])


def bullet(text, styles):
    return Paragraph(f"•  {text}", styles["BulletItem"])


def cover_block(styles, main_title, sub_title, lines):
    from reportlab.platypus import Spacer
    out = [
        Spacer(1, 2.2 * cm),
        Paragraph("CMS 原型系统", styles["CoverTitle"]),
        Spacer(1, 0.2 * cm),
        HRFlowable(
            width="55%", thickness=1.3, color=ACCENT,
            spaceBefore=6, spaceAfter=12, hAlign="CENTER",
        ),
        Paragraph(main_title, styles["CoverTitle"]),
        Spacer(1, 0.4 * cm),
    ]
    for line in lines:
        out.append(Paragraph(line, styles["CoverSub"]))
    out.append(Spacer(1, 0.7 * cm))
    out.append(Paragraph(sub_title, styles["Caption"]))
    return out


def toc_block(styles):
    from reportlab.platypus import Spacer
    toc = TableOfContents()
    toc.levelStyles = [styles["TOC1"], styles["TOC2"]]
    toc.dotsMinLevel = 0
    toc.tableStyle = TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ])
    return [
        Paragraph("目　录", styles["TocTitle"]),
        HRFlowable(width="100%", thickness=0.8, color=LINE, spaceBefore=2, spaceAfter=14),
        toc,
    ]


def build_pdf(out_path, story_factory, *, header_left, header_right, title, author):
    """两遍 multiBuild：先算总页数，再写入终稿（目录可点、页脚共 y 页）。"""
    out_path = Path(out_path)
    styles = build_styles()

    def _doc(path, page_count=None):
        doc = DocTemplate(
            str(path),
            header_left=header_left,
            header_right=header_right,
            pagesize=A4,
            leftMargin=2.15 * cm,
            rightMargin=2.15 * cm,
            topMargin=2.15 * cm,
            bottomMargin=2.05 * cm,
            title=title,
            author=author,
        )
        doc.page_count = page_count
        return doc

    tmp = out_path.with_suffix(".tmp.pdf")
    doc1 = _doc(tmp)
    doc1.multiBuild(story_factory(styles))
    total = doc1.page

    doc2 = _doc(out_path, page_count=total)
    doc2.multiBuild(story_factory(styles))
    if tmp.exists():
        tmp.unlink(missing_ok=True)

    print("SAVED", out_path)
    print("PAGES", total, "SIZE", out_path.stat().st_size)
    return out_path
