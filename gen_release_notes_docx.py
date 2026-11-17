# -*- coding: utf-8 -*-
# TaoMind 1.6.0 + 1.7.0 release notes + promo copy .docx generator
# Output:  C:\Users\Cyan\Desktop\TaoMind_1.6_1.7_ReleaseNotes.docx
# All features referenced are verified in source / git log:
#   1.6.0 (build 47-49): 81-chapter commentary + 3 free + Library 3-hub
#   1.7.0 (build 50):    Personalized Daily Verse (4 moods, cache-first LLM)

import os
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# -------- helpers --------

def set_cell_bg(cell, color_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color_hex)
    tc_pr.append(shd)


def set_cell_text_color(cell, color_hex):
    for p in cell.paragraphs:
        for run in p.runs:
            run.font.color.rgb = RGBColor.from_string(color_hex)


def _yahei(run):
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), "Microsoft YaHei")


def add_heading(doc, text, level=1, color="2b2b26"):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = RGBColor.from_string(color)
        run.font.name = "Microsoft YaHei"
        _yahei(run)
    return h


def add_para(doc, text, bold=False, size=11, color="2b2b26", align=None, italic=False):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)
    run.font.name = "Microsoft YaHei"
    _yahei(run)
    return p


def add_bullet(doc, text, size=11, indent_cm=0.5):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Cm(indent_cm)
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.name = "Microsoft YaHei"
    _yahei(run)
    run.font.color.rgb = RGBColor.from_string("2b2b26")
    return p


def add_kv_table(doc, rows, col_widths=None):
    n_cols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=n_cols)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    if col_widths:
        for i, w in enumerate(col_widths):
            for cell in table.columns[i].cells:
                cell.width = Cm(w)
    for i, row in enumerate(rows):
        for c_i, val in enumerate(row):
            cell = table.rows[i].cells[c_i]
            cell.text = ""
            run = cell.paragraphs[0].add_run(str(val))
            run.font.size = Pt(10)
            run.font.name = "Microsoft YaHei"
            _yahei(run)
            set_cell_text_color(cell, "2b2b26")
            if c_i == 0:
                run.font.bold = True
                set_cell_bg(cell, "f1ede1")
            elif i % 2 == 0:
                set_cell_bg(cell, "faf8f2")
    return table


def add_two_col(doc, left_title, left_lines, right_title, right_lines):
    """左 CN / 右 EN 双语对照段落"""
    n = max(len(left_lines), len(right_lines))
    table = doc.add_table(rows=1 + n, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    for cell in table.columns[0].cells:
        cell.width = Cm(8.0)
    for cell in table.columns[1].cells:
        cell.width = Cm(8.0)
    # header
    for c_i, head in enumerate([left_title, right_title]):
        cell = table.rows[0].cells[c_i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(head)
        run.font.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor.from_string("ffffff")
        set_cell_text_color(cell, "ffffff")
        set_cell_bg(cell, "4a6b4a")
    # body
    for r_i in range(n):
        l = left_lines[r_i] if r_i < len(left_lines) else ""
        r = right_lines[r_i] if r_i < len(right_lines) else ""
        for c_i, txt in enumerate([l, r]):
            cell = table.rows[1 + r_i].cells[c_i]
            cell.text = ""
            run = cell.paragraphs[0].add_run(txt)
            run.font.size = Pt(10)
            run.font.name = "Microsoft YaHei"
            _yahei(run)
            set_cell_text_color(cell, "2b2b26")
            if r_i % 2 == 0:
                set_cell_bg(cell, "faf8f2")
    return table


# -------- document --------

doc = Document()

for section in doc.sections:
    section.left_margin = Cm(1.8)
    section.right_margin = Cm(1.8)
    section.top_margin = Cm(1.6)
    section.bottom_margin = Cm(1.6)

style = doc.styles["Normal"]
style.font.name = "Microsoft YaHei"
style.font.size = Pt(11)
style_rpr = style.element.get_or_add_rPr()
rfonts = style_rpr.find(qn("w:rFonts"))
if rfonts is None:
    rfonts = OxmlElement("w:rFonts")
    style_rpr.append(rfonts)
rfonts.set(qn("w:eastAsia"), "Microsoft YaHei")

# ===== title =====
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr = title.add_run("TaoMind 1.6.0 + 1.7.0 Release Notes & Promo Copy")
tr.font.size = Pt(18)
tr.font.bold = True
tr.font.color.rgb = RGBColor.from_string("2b2b26")
tr.font.name = "Microsoft YaHei"
_yahei(tr)

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr = subtitle.add_run("更新内容（中英双语） + 多渠道推广文本")
sr.font.size = Pt(11)
sr.font.italic = True
sr.font.color.rgb = RGBColor.from_string("6b6a63")
_yahei(sr)

doc.add_paragraph()

# ===== 0. 版本总览 =====
add_heading(doc, "0. 版本总览", level=1)
add_kv_table(doc, [
    ("1.6.0 (build 47–49)", "2026-09-04", "道德经 81 章精讲 + 3 章免费 + Library 3 入口 hub"),
    ("1.7.0 (build 50)", "2026-09-05", "情绪化每日经文（Personalized Daily Verse）：4 mood + LLM 选章 + 缓存复用"),
    ("开发者", "cyan0914（30 年互联网 PM，独立开发者）", "—"),
    ("当前线", "1.7.0 / build 50,已上 TestFlight", "—"),
    ("下一站", "App Store 提交（1.7.0 GA）", "—"),
], col_widths=[5.0, 3.0, 8.0])

doc.add_paragraph()

# ===== 1. What's New in App Store (双语) =====
add_heading(doc, "1. What's New（App Store 更新说明字段）", level=1)
add_para(doc, "App Store 字段上限 4000 字符。这里写的是干净版，可直接复制粘贴。",
         italic=True, size=10, color="6b6a63")

# 1.6.0 单独写
add_heading(doc, "1.1  1.6.0 (build 47–49)", level=2, color="4a6b4a")
add_two_col(doc, "中文", [
    "新增 81 章道德经精讲：每一章配 6 段（原文 + 朗读 / 白话通释 / 反常识点 / 30 年 PM 真实场景 / 与上一章的张力 / 一句行动）。",
    "经藏页重做：现在只有 3 个清晰的入口——《道德经》原文（81 章）/《金刚经》原文（32 章）/《道德经》精讲（Pro）。",
    "前 3 章精讲免费试读；之后第 4 章起需要 Pro。",
    "原文书库前 5 章免费试读，第 6 章起需要 Pro。",
    "iPad 全屏适配 + 列表底部安全留白修整。",
], "English", [
    "New: 81-chapter Tao Te Ching commentary. Each chapter now has six sections — original text + audio, plain-language explanation, a counter-intuitive point, a real-life scene from a 30-year product manager, the tension with the previous chapter, and one action to take today.",
    "Library rebuilt around three clear entries: Tao Te Ching (81 original chapters), Diamond Sutra (32), and Tao Te Ching In-Depth (Pro).",
    "First 3 commentary chapters are free; chapter 4 onward is Pro.",
    "First 5 chapters of the original-text library are free; chapter 6 onward is Pro.",
    "iPad full-screen layout and bottom safe-area padding fixed.",
])

doc.add_paragraph()

# 1.7.0 单独写
add_heading(doc, "1.2  1.7.0 (build 50)", level=2, color="4a6b4a")
add_two_col(doc, "中文", [
    "全新功能：情绪化每日经文。每天打开 app，点一下你今天的心情——平静 / 烦躁 / 卡住 / 期待。",
    "AI 会从《道德经》和《金刚经》113 章里挑一句对症的经文，再写一段 2 行的私人反思。",
    "经文卡片的 eyebrow 会从「TODAY'S VERSE」变成「TODAY'S VERSE · FOR YOU」（红色），一眼看出今天这句是为你定制的。",
    "Pro 用户每日 1 次定制；新装前 3 个日历日免费体验；Day 4 起非 Pro 用户会看到升级引导。",
    "每日 8am 推送继续生效，Pro 用户的推送会复用今日缓存的定制经文。",
    "后台错误全部静默降级：网络断 / 后端抖 / LLM 输出格式异常——都会自动回退到固定经文，不会出现空白卡。",
], "English", [
    "New: Personalized Daily Verse. Each morning, tap how you feel — Calm, Restless, Stuck, or Hopeful.",
    "TaoMind reads your mood and the last seven days of reflections, then picks a verse from the Tao Te Ching or Diamond Sutra and writes a two-line personal reflection for you.",
    "When a verse is personalized, the card eyebrow shifts to a red TODAY'S VERSE · FOR YOU — so you know it was chosen for you, not rotated in.",
    "Pro members get one personalized verse every day. New users get the first three calendar days as a free trial. From day four, free users see a soft upgrade prompt instead.",
    "The 8am daily push notification still works. For Pro users, the notification reuses today's cached personalized verse when present.",
    "Quiet fallback: offline, backend hiccup, or LLM-format drift all degrade silently to the fixed daily verse. You will never see a blank card.",
])

doc.add_paragraph()

# 1.6 + 1.7 combined (for next App Store "What's New" submission)
add_heading(doc, "1.3  合并版 What's New（下次 App Store 提交用）", level=2, color="4a6b4a")
add_para(doc, "App Store 字段。直接复制 → Connect → 版本信息 → 推广文本 → What's New。",
         italic=True, size=10, color="6b6a63")

add_heading(doc, "中文（合并 1.6.0 + 1.7.0）", level=3, color="6b6a63")
add_para(doc, "这一版我们做了两件大事：把「经藏」从 194 章的长列表重做成 3 个清晰的入口，并且——"
              "新装前 3 天免费、Pro 每天 1 次——让你每天打开 app 时,app 已经在心里为你挑好了一句对症的经文。",
         size=11)
add_bullet(doc, "1.6.0：道德经 81 章精讲上线，每章 6 段：原文 + 朗读 / 白话通释 / 反常识点 / 30 年 PM 真实场景 / 与上一章的张力 / 一句行动。")
add_bullet(doc, "1.6.0：经藏改 3 入口 hub——《道德经》原文（81 章）/《金刚经》原文（32 章）/《道德经》精讲（Pro）。")
add_bullet(doc, "1.6.0：精讲前 3 章免费、原文前 5 章免费——让你先尝后买。")
add_bullet(doc, "1.7.0（新）：情绪化每日经文——点今天的心情（平静/烦躁/卡住/期待），AI 帮你从 113 章里挑一句经文 + 写 2 行反思。")
add_bullet(doc, "1.7.0（新）：经文卡 eyebrow 变红色「TODAY'S VERSE · FOR YOU」——一眼看出今天的经文是为你选的。")
add_bullet(doc, "1.7.0（新）：8am 推送会复用今日定制的经文，Pro 用户每天都收到一句合你当下状态的。")

doc.add_paragraph()

add_heading(doc, "English (1.6.0 + 1.7.0 combined)", level=3, color="6b6a63")
add_para(doc, "This update does two things. We rebuilt the Library from a 194-chapter wall into three clear entries, "
              "and we added something we wish every meditation app had: a verse that knows how you feel this morning. "
              "New users get the first three days free; Pro members get one personalized verse every day.", size=11)
add_bullet(doc, "1.6.0 — 81-chapter Tao Te Ching commentary is live. Each chapter has six sections: original verse + audio, plain-language meaning, a counter-intuitive point, a real scene from a 30-year product manager, the tension with the previous chapter, and one action for today.")
add_bullet(doc, "1.6.0 — The Library is now three clear entries: Tao Te Ching (81 original), Diamond Sutra (32), and Tao Te Ching In-Depth (Pro).")
add_bullet(doc, "1.6.0 — The first 3 commentary chapters and the first 5 original-text chapters are free. Try before you buy.")
add_bullet(doc, "1.7.0 (new) — Personalized Daily Verse. Tap how you feel — Calm, Restless, Stuck, or Hopeful — and TaoMind picks a verse from 113 chapters and writes a two-line reflection.")
add_bullet(doc, "1.7.0 (new) — Personalized cards now show a red TODAY'S VERSE · FOR YOU eyebrow, so you can tell at a glance which verses were chosen for you.")
add_bullet(doc, "1.7.0 (new) — The 8am daily push notification reuses today's personalized verse, so Pro members get a verse that actually fits their morning.")

doc.add_paragraph()

# ===== 2. App Store Description (双语) =====
add_heading(doc, "2. App Store Description（产品描述字段）", level=1)
add_para(doc, "字段上限 4000 字符。供下次提交用。",
         italic=True, size=10, color="6b6a63")

add_heading(doc, "2.1  中文版", level=2, color="4a6b4a")
add_para(doc, "TaoMind 是给 30+ 岁、每天被工作压得喘不过气的人用的「东方智慧口袋本」。", size=11)
add_para(doc, "我们不做鸡汤，不做冥想引导，不做打卡 KPI。我们做一件事：把《道德经》和《金刚经》里最经典的 113 章,"
              "用 30 年互联网 PM 的真实场景重讲一遍,让你在地铁上、午休时、深夜哄完孩子以后,"
              "3 分钟能读到一句当下合用的经文 + 2 行反思 + 1 件今天就能做的小事。", size=11)
add_para(doc, "——本次更新——", bold=True, size=12)
add_bullet(doc, "81 章道德经精讲：原文 + 朗读 + 通释 + 反常识点 + 30 年 PM 场景 + 张力 + 一句行动。")
add_bullet(doc, "经藏 3 入口：《道德经》原文（81 章）/《金刚经》原文（32 章）/《道德经》精讲（Pro）。")
add_bullet(doc, "情绪化每日经文（Pro 每日 1 次，新装前 3 天免费体验）：点今天的心情，AI 帮你从 113 章里挑一句对症的。")
add_bullet(doc, "寻求智慧：把当下的烦恼写下来，AI 从经文里挑 1 段 + 写解释 + 给你 1 件今天能做的小事。")
add_bullet(doc, "Pro 完整解锁：81 章精讲全开 / 113 章原文 / 无限求取 / 风格调节 / 月度修习报告 / 日志导出。")
add_para(doc, "App Store 搜「TaoMind」下载。", italic=True, size=10, color="6b6a63")

doc.add_paragraph()

add_heading(doc, "2.2  English", level=2, color="4a6b4a")
add_para(doc, "TaoMind is a pocket companion for the 30-something professional who has tried Headspace, "
              "finished Waking Up, and still wants something that does not feel American.", size=11)
add_para(doc, "We do not do motivational quotes. We do not do guided meditation. We do not gamify your streak. "
              "We do one thing: take the 113 most-quoted chapters of the Tao Te Ching and the Diamond Sutra, "
              "and re-explain them through the lived experience of a 30-year internet product manager. "
              "Three minutes on the subway, three minutes at lunch, three minutes after the kids are down — "
              "one verse, two lines of reflection, one small thing to do today.", size=11)
add_para(doc, "What's in this update", bold=True, size=12)
add_bullet(doc, "81-chapter Tao Te Ching commentary — original verse + audio, plain-language meaning, a counter-intuitive point, a real PM scene, the tension with the previous chapter, and one action for today.")
add_bullet(doc, "Library rebuilt around three clear entries: Tao Te Ching (81 original), Diamond Sutra (32), and Tao Te Ching In-Depth (Pro).")
add_bullet(doc, "Personalized Daily Verse (Pro daily, free for new users' first 3 days) — tap your mood, TaoMind picks a verse from 113 chapters and writes a two-line reflection.")
add_bullet(doc, "Seek Wisdom — type what's bothering you, and TaoMind responds with a passage, an explanation, a reflection, and one small thing to do today.")
add_bullet(doc, "Pro unlocks everything: all 81 commentary chapters, all 113 original chapters, unlimited Seek Wisdom, response-style tuning, monthly practice report, journal export.")
add_para(doc, "Search 'TaoMind' on the App Store.", italic=True, size=10, color="6b6a63")

doc.add_paragraph()

# ===== 3. Promo copy (推广文本) =====
add_heading(doc, "3. 推广文本（多渠道）", level=1)
add_para(doc, "以下分 5 个渠道,直接复制即用。",
         italic=True, size=10, color="6b6a63")

# 3.1 微博 / 小红书 / 抖音 caption
add_heading(doc, "3.1  微博 / 小红书 / 抖音（中文·200 字内）", level=2, color="4a6b4a")
add_para(doc, "把 2500 年的《道德经》,变成你今天能用的智慧。", bold=True, size=12)
add_para(doc, "TaoMind 1.7 上线：", size=11)
add_bullet(doc, "点今天的心情（平静/烦躁/卡住/期待）→ AI 帮你从 113 章里挑一句对症的经文 + 写 2 行反思。")
add_bullet(doc, "81 章道德经精讲：原文 + 通释 + 反常识点 + 30 年 PM 真实场景。")
add_bullet(doc, "新装前 3 天免费体验；Pro 每天 1 次定制。")
add_para(doc, "适合人群：30+ 互联网人,读不进原文,想要 3 分钟就能用的东方智慧。", size=11)
add_para(doc, "App Store 搜「TaoMind」", bold=True, size=11)
add_para(doc, "#道德经 #TaoTeChing #冥想 #东方哲学 #iPhoneApp", italic=True, size=10, color="6b6a63")

doc.add_paragraph()

# 3.2 Twitter / X
add_heading(doc, "3.2  Twitter / X（英文·280 字符内）", level=2, color="4a6b4a")
add_para(doc, "TaoMind 1.7 just shipped. Big change:", bold=True, size=12)
add_bullet(doc, "Tap your morning mood (Calm / Restless / Stuck / Hopeful).")
add_bullet(doc, "TaoMind picks a verse from 113 chapters + writes a 2-line reflection.")
add_bullet(doc, "81-chapter Tao Te Ching commentary is now live (Pro).")
add_para(doc, "New users get the first 3 days free. Pro members get one personalized verse every day.", size=11)
add_para(doc, "Search 'TaoMind' on the App Store.", bold=True, size=11)
add_para(doc, "#TaoTeChing #DiamondSutra #meditation #iPhoneApp", italic=True, size=10, color="6b6a63")

doc.add_paragraph()

# 3.3 LinkedIn / 邮件签名
add_heading(doc, "3.3  LinkedIn / 邮件签名（英文·专业感）", level=2, color="4a6b4a")
add_para(doc, "I shipped two updates to TaoMind this week. TaoMind is an iOS app for working professionals who want "
              "Eastern wisdom that actually fits their day — not 30 minutes of guided meditation, but 3 minutes of "
              "a verse, a reflection, and one small thing to do today.", size=11)
add_para(doc, "1.6.0 brings 81-chapter Tao Te Ching commentary — each chapter now has 6 sections: original + audio, "
              "plain-language meaning, a counter-intuitive point, a real PM scene, the tension with the previous "
              "chapter, and one action to take.", size=11)
add_para(doc, "1.7.0 adds Personalized Daily Verse — tap your mood each morning, TaoMind reads your last 7 days of "
              "reflections and picks a verse that fits. New users get the first 3 days free; Pro members get one "
              "personalized verse every day.", size=11)
add_para(doc, "Try it on the App Store: search 'TaoMind'. Link in bio.", italic=True, size=10, color="6b6a63")

doc.add_paragraph()

# 3.4 Founder video 描述（配合刚写完的 TikTok 脚本）
add_heading(doc, "3.4  创始人 TikTok 视频描述（中文 / English）", level=2, color="4a6b4a")
add_para(doc, "对应：C:\\Users\\Cyan\\Desktop\\TaoMind_TikTok_Video1_Script.docx", italic=True, size=10, color="6b6a63")

add_heading(doc, "中文", level=3, color="6b6a63")
add_para(doc, "30 年互联网 PM 做了 1 个 app：把 2500 年的《道德经》,变成你今天能用的智慧。", bold=True, size=12)
add_para(doc, "——这一版——", size=11)
add_bullet(doc, "1.6.0: 81 章道德经精讲上线,每章 6 段。")
add_bullet(doc, "1.7.0: 点今天的心情,AI 帮你从 113 章里挑一句对症的经文 + 写 2 行反思（Pro 每日 1 次,新装前 3 天免费）。")
add_para(doc, "适合：读不进原文,想要 3 分钟就能用的东方智慧的人。", size=11)
add_para(doc, "App Store 搜「TaoMind」· 链接在主页", bold=True, size=11)
add_para(doc, "#道德经 #TaoTeChing #冥想 #东方哲学 #iPhoneApp #founder", italic=True, size=10, color="6b6a63")

doc.add_paragraph()

add_heading(doc, "English", level=3, color="6b6a63")
add_para(doc, "A 30-year PM built an app that turns 2,500 years of Tao Te Ching into today's wisdom.", bold=True, size=12)
add_para(doc, "What's new:", size=11)
add_bullet(doc, "1.6.0: 81-chapter Tao Te Ching commentary is live — each chapter has 6 sections.")
add_bullet(doc, "1.7.0: Personalized Daily Verse. Tap your mood, TaoMind picks a verse from 113 chapters + writes a 2-line reflection. Pro daily, free for new users' first 3 days.")
add_para(doc, "For: people who can't read the original, but want Eastern wisdom in 3 minutes.", size=11)
add_para(doc, "Search 'TaoMind' on the App Store · Link in bio", bold=True, size=11)
add_para(doc, "#TaoTeChing #meditation #iPhoneApp #founder", italic=True, size=10, color="6b6a63")

doc.add_paragraph()

# 3.5 ProductHunt launch (下周或合适时机)
add_heading(doc, "3.5  Product Hunt Launch Copy（英文·launch day）", level=2, color="4a6b4a")
add_para(doc, "Tagline (60 字符内):", bold=True, size=11)
add_para(doc, "Eastern wisdom for working professionals, 3 minutes a day.", italic=True, size=11)

add_para(doc, "Short description (260 字符内):", bold=True, size=11)
add_para(doc, "TaoMind is an iOS app that re-explains the Tao Te Ching and the Diamond Sutra "
              "through a 30-year PM's real experience. New: tap your morning mood, get a verse that "
              "actually fits. 81-chapter commentary is now live.", italic=True, size=11)

add_para(doc, "Long description:", bold=True, size=11)
add_para(doc, "Hi PH 👋 I built TaoMind for working professionals who want Eastern wisdom that fits their day, "
              "not a 30-minute guided meditation session.", size=11)
add_para(doc, "Three things make TaoMind different:", size=11)
add_bullet(doc, "81-chapter commentary. Each chapter has 6 sections: original verse + audio, plain-language meaning, a counter-intuitive point, a real-life scene from a 30-year product manager, the tension with the previous chapter, and one action to take today.")
add_bullet(doc, "Personalized Daily Verse. Tap how you feel (Calm / Restless / Stuck / Hopeful), TaoMind reads your last 7 days of reflections and picks a verse from 113 chapters that fits.")
add_bullet(doc, "Seek Wisdom. Type what's bothering you, get a passage + explanation + reflection + one small thing to do today.")
add_para(doc, "Free tier: 3 days trial + first 3 commentary chapters + first 5 original-text chapters. "
              "Pro: everything, $X.99/year or $Y.99 lifetime.", size=11)
add_para(doc, "Built solo by a 30-year internet PM. I would love your feedback.", italic=True, size=11)

doc.add_paragraph()

# 3.6 Reddit / 社区
add_heading(doc, "3.6  Reddit / 社区帖（中文·r/taoism 等）", level=2, color="4a6b4a")
add_para(doc, "标题:做了 1 个 iOS app,30 年 PM 视角的《道德经》精讲 + 每日定制经文", bold=True, size=12)
add_para(doc, "我做了 1 个 iOS app：TaoMind。", size=11)
add_para(doc, "做它的原因：我读完市面上大部分冥想 app,觉得对 30+ 互联网人都不太对——"
              "要么是西式引导冥想,要么是把《道德经》当壁纸图。我想要的是:"
              "在地铁上 3 分钟,读到一句当下合用的经文 + 2 行反思 + 1 件今天就能做的小事。", size=11)
add_para(doc, "这一版更新了两个东西:", size=11)
add_bullet(doc, "81 章道德经精讲:每章 6 段(原文/通释/反常识点/30 年 PM 场景/张力/一句行动),前 3 章免费。")
add_bullet(doc, "情绪化每日经文:点今天的心情,AI 帮你从 113 章里挑一句对症的经文(Pro 每日 1 次,新装前 3 天免费)。")
add_para(doc, "我不是搞学术的,做的是「30 年 PM 视角下的东方智慧」——所以通释里讲的是怎么用这章经文去处理 deadline、"
              "下属离职、跨部门撕逼,而不是训诂学。", size=11)
add_para(doc, "免费层够用,不强求订阅。链接在 App Store,搜「TaoMind」。欢迎反馈。", italic=True, size=10, color="6b6a63")

doc.add_paragraph()

# ===== 4. ASO 关键词建议 =====
add_heading(doc, "4. ASO 关键词建议", level=1)
add_para(doc, "App Store 关键词字段 100 字符内（英文）。", italic=True, size=10, color="6b6a63")
add_kv_table(doc, [
    ("英文 keyword 字段", "taoism,tao,tao te ching,diamond sutra,meditation,zen,buddhism,stoic,wisdom,daily verse,anxiety,calm,reflection,stoicism,philosophy"),
    ("中文 keyword 字段", "道德经,金刚经,冥想,禅,国学,东方哲学,古籍,佛经,道家,智慧,减压,焦虑,反思,日记,打卡"),
    ("推荐 Title", "TaoMind — Daily Tao Te Ching"),
    ("推荐 Subtitle", "Personalized wisdom for working life"),
], col_widths=[3.5, 13.0])

doc.add_paragraph()

# footer
foot = doc.add_paragraph()
foot.alignment = WD_ALIGN_PARAGRAPH.RIGHT
fr = foot.add_run("基于 git log + iOS 源码核对 · 2026-09-06")
fr.font.size = Pt(9)
fr.font.italic = True
fr.font.color.rgb = RGBColor.from_string("9a9890")
_yahei(fr)

# save
out_path = r"C:\Users\Cyan\Desktop\TaoMind_1.6_1.7_ReleaseNotes.docx"
doc.save(out_path)
print("Saved: " + out_path)
print("Size: " + str(os.path.getsize(out_path)) + " bytes")
