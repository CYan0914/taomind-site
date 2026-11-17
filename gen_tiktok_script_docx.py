# -*- coding: utf-8 -*-
# TaoMind founder TikTok #1 video — full script + recording action table .docx generator
# Output:  C:\Users\Cyan\Desktop\TaoMind_TikTok_Video1_Script.docx
# All UI actions correspond to real iOS views (verified against source):
#   PracticeView, LibraryView, LibraryJingjiangView, JingjiangDetailView,
#   LibrarySourceView, LibraryDetailView, SeekWisdomView, WisdomResultView,
#   PaywallView, SubscriptionManager.

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


def add_action_table(doc, rows):
    headers = ["#", "起始时间", "屏幕", "UI 元素", "动作 (手指)", "镜头 / 字幕"]
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    widths_cm = [0.8, 1.6, 2.5, 3.5, 4.5, 4.0]
    for i, w in enumerate(widths_cm):
        for cell in table.columns[i].cells:
            cell.width = Cm(w)
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        run.font.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor.from_string("ffffff")
        set_cell_text_color(cell, "ffffff")
        set_cell_bg(cell, "4a6b4a")
    for r_i, row in enumerate(rows, start=1):
        for c_i, val in enumerate(row):
            cell = table.rows[r_i].cells[c_i]
            cell.text = ""
            run = cell.paragraphs[0].add_run(str(val))
            run.font.size = Pt(9)
            run.font.name = "Microsoft YaHei"
            _yahei(run)
            set_cell_text_color(cell, "2b2b26")
            if r_i % 2 == 0:
                set_cell_bg(cell, "faf8f2")
    return table


# -------- document --------

doc = Document()

for section in doc.sections:
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)
    section.top_margin = Cm(1.8)
    section.bottom_margin = Cm(1.8)

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
tr = title.add_run("TaoMind 创始人 TikTok 第 1 支视频")
tr.font.size = Pt(20)
tr.font.bold = True
tr.font.color.rgb = RGBColor.from_string("2b2b26")
tr.font.name = "Microsoft YaHei"
_yahei(tr)

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr = subtitle.add_run("完整文案（中英双轨字幕）+ 录屏动作表 · 60–75s · 纯 demo 背景音 · 无旁白")
sr.font.size = Pt(11)
sr.font.italic = True
sr.font.color.rgb = RGBColor.from_string("6b6a63")
_yahei(sr)

doc.add_paragraph()

# ===== 0. overview =====
add_heading(doc, "0. 视频总览", level=1)
add_kv_table(doc, [
    ("账号", "@cyanbuilds（创始人 / 工程师，30 年互联网 PM）"),
    ("视频主题", "TaoMind 新版本（build 50）功能介绍：道德经精讲 + 原文书库 + 寻求智慧 + 会员"),
    ("目标时长", "65–72 秒（落在 2026 算法推荐的 60–75s 完播率甜区）"),
    ("画幅", "9:16 竖屏 1080×1920，安全条中央 880px 宽，文字 / logo 不贴边缘"),
    ("声音", "纯 demo 背景音（无旁白）—— App 内 UI 触感音 + 一段轻古风 BGM（音量 ≤ 0.18）"),
    ("字幕", "中英双轨：每段同时给中文 + 英文两行字幕，画面下方 1/3 区域"),
    ("Hook 类型", "陈述型（A）：第一帧就甩一句有立场的结论，让用户知道看完能得到什么"),
    ("节奏", "每 6–10s 切一次画面；不允许一个屏幕停留超过 12 秒"),
    ("录制设备", "iPhone 真机（已通过 TestFlight 装 build 50）"),
    ("录屏工具", "iOS 屏幕录制（控制中心长按录屏按钮）或第三方 ProMovie / Filmic Pro"),
], col_widths=[3.0, 13.0])

doc.add_paragraph()

# ===== 1. structure =====
add_heading(doc, "1. 视频结构（5 段）", level=1)
add_kv_table(doc, [
    ("① Hook 陈述", "0.0–2.5s · 黑底白字 / 创始人 logo", "用 1 句结论抓住为什么这 app 值得装"),
    ("② 情绪经文 Setup", "2.5–12s · PracticeView 主屏", "展示 build 50 核心新功能：点心情 → 今日经文"),
    ("③ Demo A 精讲", "12–28s · Library → Jingjiang → Detail", "道德经 81 章精讲：从列表点进第 N 章，6 段结构逐屏下滚"),
    ("④ Demo B 原文", "28–40s · Library → Source → Detail", "道德经 / 金刚经 113 章原文 + 白话精讲 + 反思"),
    ("⑤ Demo C 求智慧", "40–54s · SeekWisdomView", "个人烦恼 → 选场景 → 写问题 → 求 → 4 段结果"),
    ("⑥ 会员介绍", "54–64s · PaywallView (从 C 末的 Pro banner 跳入)", "3 条 hero 卖点 + Pro 解锁的功能"),
    ("⑦ CTA 收尾", "64–70s · App Store 卡片 + 账号头像", "3 秒定格，引导点击主页链接下载"),
], col_widths=[3.5, 5.5, 7.0])

doc.add_paragraph()

# ===== 2. full script =====
add_heading(doc, "2. 完整文案（中英双轨字幕 + 画面说明）", level=1)
add_para(doc, "规则：每段同时显示中英双轨字幕（中文在上英文在下，14pt 白色 + 1pt 黑描边）。"
              "无旁白，背景音 = UI 触感音 + 一段 BGM 循环。",
         italic=True, color="6b6a63", size=10)

# Q = opening Chinese curly quote, Z = closing
LQ = "“"  # “
RQ = "”"  # ”

script_sections = [
    {
        "idx": "①",
        "time": "0.0–2.5s",
        "title": "Hook 陈述",
        "scene": "黑底，纯白大字，居中。结尾切到 founder 头像 0.3s 闪回。",
        "cn_sub": "把 2500 年的《道德经》，变成你今天能用的智慧。",
        "en_sub": "Turn 2,500 years of Tao Te Ching into today's wisdom.",
        "bgm": "BGM 0.5s 起音（不抢先）",
    },
    {
        "idx": "②",
        "time": "2.5–12s",
        "title": "情绪经文（build 50 核心新功能）",
        "scene": "PracticeView 主屏。手指依次点 4 个 mood chip，最后停在一个被选中的 chip 上 + 当日经文卡 eyebrow 变 " + LQ + "TODAY'S VERSE · FOR YOU" + RQ + "。",
        "cn_sub": "新功能：点今天的心情，app 自动从 113 章里为你挑一句对症的经文。",
        "en_sub": "New: tap today's mood, and TaoMind picks the verse that fits.",
        "bgm": "chip 选中声（系统触感音）",
    },
    {
        "idx": "③",
        "time": "12–28s",
        "title": "Demo A · 道德经精讲",
        "scene": "Tab 切到「经藏」Library → 看到 3 个入口卡：道德经原文 / 金刚经原文 / 道德经精讲（带 PRO 角标）。"
                "手指点第 3 张 → 滚到第 8 章（有 PRO 锁图标）→ 弹付费墙；关掉付费墙 → 滚到第 1 章（免费预览）→ 进 detail → "
                "慢慢下滚 6 段：原文 + 播放音频按钮 / 通释 / 反常识点 / 30 年 PM 场景 / 张力 / 一句行动。",
        "cn_sub": "81 章精讲：原文 + 白话通释 + 反常识点 + 30 年 PM 的真实场景。",
        "en_sub": "81-chapter commentary: original text, plain meaning, counter-intuitive insight, a 30-year PM's real scene.",
        "bgm": "音频播放按钮 0.8s 起（真放 1 段音频）",
    },
    {
        "idx": "④",
        "time": "28–40s",
        "title": "Demo B · 道德经 / 金刚经原文书库",
        "scene": "返回 Library → 点「道德经原文」→ 看到 81 章列表（前 5 章免费，后续带锁）→ 点第 1 章 → 进 detail："
                "显示原文大字体（Georgia 斜体）+ Commentary + Reflection。",
        "cn_sub": "道德经 81 章 + 金刚经 32 品，原文 + 白话 + 反思，全部一站读完。",
        "en_sub": "Tao Te Ching 81 + Diamond Sutra 32. Original, commentary, reflection — all in one place.",
        "bgm": "列表滚动声",
    },
    {
        "idx": "⑤",
        "time": "40–54s",
        "title": "Demo C · 寻求智慧（个人烦恼 → 4 段回应）",
        "scene": "Tab 切到「求智慧」SeekWisdomView → 滚到中段：选「Personal」场景 chip → TextEditor 里写 "
                + LQ + "My team is burning out from constant deadlines" + RQ + "（预填好不真敲）→ 点「求」印章按钮 → 等待 → "
                "4 段结果依次淡入：Passage / Wisdom / Reflection / Way Forward → 滚到结果末尾，看到 Pro banner（想不限次？）→ 点 banner 跳付费墙。",
        "cn_sub": "把你的烦恼写下来，AI 从 113 章里挑经文 + 写解释 + 给你一条今天能做的小事。",
        "en_sub": "Type your struggle. TaoMind picks a verse, explains it, gives you one small thing to do today.",
        "bgm": "印章按下声 + 4 段结果淡入节奏",
    },
    {
        "idx": "⑥",
        "time": "54–64s",
        "title": "会员介绍（PaywallView）",
        "scene": "付费墙从下弹入。滚到中段：3 条 hero 卖点（名师 / 不限次 / 月度补卡）→ 继续滚展示 6 条完整功能"
                "（无限日志 / 完整经藏 / 里程碑卡片 / 月报 / 风格调节 / 导出）→ 显示 plan 选项（年档置顶 + BEST VALUE 角标）。",
        "cn_sub": "Pro 解锁：无限求取 · 完整精讲 · 每日情绪定制 · 风格调节 · 月报 · 导出。",
        "en_sub": "Pro unlocks: unlimited seeks, full commentary, daily personalized verse, style tuning, monthly report, export.",
        "bgm": "BGM 升调 0.5s 强调",
    },
    {
        "idx": "⑦",
        "time": "64–70s",
        "title": "CTA 收尾",
        "scene": "硬切回 PracticeView 主屏定格 1s（已为今日定制 ✓ 那一行）→ 黑底白字 + 创始人头像 + App Store 标志 + 主页链接。",
        "cn_sub": "App Store 搜「TaoMind」· 链接在主页",
        "en_sub": "Search 'TaoMind' on App Store · Link in bio",
        "bgm": "BGM 0.5s 渐隐",
    },
]

for sec in script_sections:
    add_heading(doc, sec["idx"] + " " + sec["title"] + "  [" + sec["time"] + "]", level=2, color="4a6b4a")
    add_para(doc, "画面：" + sec["scene"], size=10, color="6b6a63")
    add_kv_table(doc, [
        ("中文字幕", sec["cn_sub"]),
        ("英文字幕", sec["en_sub"]),
        ("BGM / 音", sec["bgm"]),
    ], col_widths=[2.8, 13.5])
    doc.add_paragraph()

# ===== 3. action table =====
add_heading(doc, "3. 录屏动作表（按时间顺序，逐拍）", level=1)
add_para(doc, "每行 = 一拍镜头。# 是动作序号，镜头时长通常 1.5–4s。",
         italic=True, size=10, color="6b6a63")

actions = [
    (1, "0.0s", "黑底", "全屏文字", "录屏开始即定格；不操作", "中文大字 + 英文小字堆叠，居中"),
    (2, "2.0s", "黑底", "右下角 logo", "不操作", "TaoMind logo + founder 头像 0.5s 闪回"),
    (3, "2.5s", "PracticeView", "streak header", "不操作（app 已登录 Pro 账户）", "进首页，eyebrow 显 TODAY'S VERSE + verse 卡片"),
    (4, "4.0s", "PracticeView", "mood row 4 chip", "手指点第 1 个 chip「😐 Calm」", "chip 选中：1.5pt bronze 描边 + 浅填充"),
    (5, "5.5s", "PracticeView", "mood row", "手指点第 3 个 chip「😤 Restless」", "切心情：第 1 个 chip 取消高亮，第 3 个高亮"),
    (6, "7.0s", "PracticeView", "verse 卡片 eyebrow", "不操作", "卡片上方 eyebrow 从 TODAY'S VERSE 变成 TODAY'S VERSE · FOR YOU 红色（build 50 行为）"),
    (7, "9.0s", "PracticeView", "verse 卡片", "向上慢慢滑动 1s 看完整张卡", "展示今日经文 + reflection（先已 cache，无 spinner）"),
    (8, "11.0s", "PracticeView", "底部 tab bar", "手指点「Library」图标", "切到经藏页"),
    (9, "11.5s", "LibraryView", "3 个 hub card", "静止 1s", "第 3 张卡「道德经精讲」右侧有 PRO 角标"),
    (10, "12.5s", "LibraryView", "第 3 张 hub card", "手指点「道德经精讲」", "导航推入 LibraryJingjiangView"),
    (11, "13.5s", "LibraryJingjiangView", "chapter list", "向上滑 2s", "滚到第 5 章以后，看到每行带 🔒 锁图标"),
    (12, "15.5s", "LibraryJingjiangView", "第 8 章 (锁定)", "手指点第 8 章", "弹付费墙（.jingjiangLocked 场景条）"),
    (13, "16.5s", "PaywallView (modal)", "顶部场景条", "不操作", "展示 试读结束 · 道德经·精讲 金色场景条"),
    (14, "17.5s", "PaywallView", "顶部", "手指点左上 ✕", "关闭付费墙，返回列表"),
    (15, "18.5s", "LibraryJingjiangView", "第 1 章", "手指点「第 1 章」", "sheet 推入 JingjiangDetailView"),
    (16, "19.5s", "JingjiangDetailView", "原文 + 音频按钮", "手指点 ▶ 播放按钮 1s 后暂停", "播放按钮变 ⏸ + 状态行变暂停；BGM 音量降 0.5"),
    (17, "21.0s", "JingjiangDetailView", "通释 section", "向上滑 2s", "展示「Commentary」白话通释"),
    (18, "23.0s", "JingjiangDetailView", "反常识点", "继续上滑 1.5s", "展示 bronze 描边 callout 块"),
    (19, "24.5s", "JingjiangDetailView", "张力 section", "继续上滑 1.5s", "展示「与上一章的张力」"),
    (20, "26.0s", "JingjiangDetailView", "一句行动", "继续上滑 1.5s", "朱砂色按钮 一句行动 带 figure.walk 图标"),
    (21, "27.5s", "LibraryJingjiangView", "左上 ←", "手指点返回", "回到 LibraryView"),
    (22, "28.5s", "LibraryView", "第 1 张 hub card", "手指点「道德经原文」", "推入 LibrarySourceView(81 章)"),
    (23, "30.0s", "LibrarySourceView", "第 1 章", "手指点「第 1 章」", "sheet 推入 LibraryDetailView"),
    (24, "31.0s", "LibraryDetailView", "原文 verse", "向上滑 2.5s", "展示 Georgia 斜体大字原文 + Commentary 卡片 + Reflection"),
    (25, "33.5s", "LibraryDetailView", "底部", "手指点左上 ← 关掉", "回到 LibrarySourceView"),
    (26, "35.0s", "LibrarySourceView", "左上 ←", "手指点返回", "回到 LibraryView"),
    (27, "36.0s", "LibraryView", "底部 tab", "手指点「Seek Wisdom」", "切到 SeekWisdomView"),
    (28, "37.0s", "SeekWisdomView", "顶部 daily verse", "向上滑 2s", "展示 daily verse banner（可点收起的）"),
    (29, "39.0s", "SeekWisdomView", "scenario chip 行", "手指点「Personal」chip", "chip 变深底白字"),
    (30, "40.0s", "SeekWisdomView", "TextEditor", "不操作（已预填 My team is burning out from constant deadlines）", "展示预填的英文问题"),
    (31, "42.0s", "SeekWisdomView", "「求」印章按钮", "手指点 朱砂 求 印章", "按钮变 busy（spinner）"),
    (32, "44.0s", "SeekWisdomView", "4 段结果", "静止 3s 等结果", "Passage / Wisdom / Reflection / Way Forward 依次淡入"),
    (33, "47.0s", "SeekWisdomView", "结果末尾 Pro banner", "向上滑 1s 看 banner", "展示 想不限次？解锁 TaoMind Premium 金色 banner"),
    (34, "48.5s", "SeekWisdomView", "Pro banner", "手指点 banner", "弹付费墙（.seekResult 场景）"),
    (35, "49.5s", "PaywallView", "场景条", "不操作 1s", "展示 刚收到一条回应 · 心流转化位 金色场景条"),
    (36, "50.5s", "PaywallView", "3 条 hero", "向上滑 1.5s", "展示 名师 / 不限次 / 月度补卡"),
    (37, "52.0s", "PaywallView", "6 条 feature", "继续上滑 1.5s", "展示 完整功能清单"),
    (38, "53.5s", "PaywallView", "plan cards", "继续上滑 1.5s", "年档置顶 + BEST VALUE 角标"),
    (39, "55.0s", "PaywallView", "顶部 ✕", "手指点 ✕", "关掉付费墙"),
    (40, "56.0s", "SeekWisdomView", "顶部 ←", "手指点返回", "回到 PracticeView"),
    (41, "57.0s", "PracticeView", "verse 卡", "静止 1s", "定格 已为今日定制 ✓ 那一行"),
    (42, "58.0s", "PracticeView", "verse 卡", "静止 1s", "定格收尾画面"),
    (43, "59.0s", "黑底", "全屏", "录屏结束", "CTA 文字：搜「TaoMind」· 主页链接"),
    (44, "62.0s", "黑底", "全屏", "录屏结束", "founder 头像 + App Store 标志 + 链接"),
    (45, "65.0s", "—", "—", "录屏结束", "总时长 65s（BGM 0.5s 渐隐，字幕保留 2s）"),
]

add_action_table(doc, actions)

doc.add_paragraph()

# ===== 4. pre-recording =====
add_heading(doc, "4. 录制前置准备", level=1)
add_kv_table(doc, [
    ("① TestFlight 安装", "确认 iPhone 装的是 build 50（1.7.0 / 50）—— PracticeView 顶部 4 个 mood chip 必须存在"),
    ("② 登录 Pro 账户", "用 founder 自己的 Pro 账户录屏，否则 Pro banner 和心境 chip 逻辑会变，演示效果打折"),
    ("③ iPhone 系统时间", "不要人为改日期（避免 Day 1-3 trial 逻辑触发），用真实今日录制"),
    ("④ 网络", "Wi-Fi 稳定；现场先点 1 次「求智慧」预热 LLM 缓存，正式录屏时 4 段结果淡入会更顺"),
    ("⑤ 通知", "iOS 设置里关掉所有其他 app 通知（避免录屏时横幅压画面）"),
    ("⑥ 屏幕亮度", "调到 70–80%，避免反光 + 让字幕白字看得清"),
    ("⑦ 横屏锁定", "控制中心关掉横屏旋转（避免误转）"),
    ("⑧ 录屏工具", "iOS 自带录屏 或 ProMovie；建议用 ProMovie，可后期直接调分辨率 + 帧率"),
    ("⑨ 字幕后期", "剪映 / CapCut 双轨字幕（中文 14pt 白色 + 1pt 黑描边，英文 11pt 白色 + 0.5pt 黑描边）"),
    ("⑩ BGM", "推荐古风低 BPM 曲（≤ 0.18 音量）；用 剪映/达芬奇混音时 UI 触感音保留 0.4 音量"),
], col_widths=[3.5, 13.0])

doc.add_paragraph()

# ===== 5. post =====
add_heading(doc, "5. 后期要点（剪映 / CapCut）", level=1)
add_kv_table(doc, [
    ("封面", "取第 1 帧黑底大字的截图；或截 PracticeView 顶格 verse 卡 eyebrow 那一行"),
    ("首帧", "必须是黑底大字，不能是 PracticeView 列表（否则用户刷到不知道在卖什么）"),
    ("字幕", "中英双轨，每段同时上；不要先中文后英文分两段播"),
    ("BGM 音量", "≤ 0.18（不能盖过 UI 触感音）"),
    ("音频预设", "BGM 起始于 0.5s，不要从 0s 起（让首帧先打字幕 0.5s 静默）"),
    ("章节速度", "3 段 demo 节奏不同：精讲慢（原速）、原文中速、求智慧快（等结果 3s 内）"),
    ("完播率钩子", "Hook 2.5s 截止必须已说出道德经 + 智慧两个关键词；否则用户划走"),
    ("CTA 收尾", "最后 5s 必须有 founder 头像 + App Store 标志（强提示来源）"),
    ("Pro 账户遮罩", "如果演示 Pro banner 时不希望露出 Pro 标签，可临时把账户切到 Free，但所有 Pro 解锁后 的功能演示就会变付费墙"),
    ("Hashtag", "建议用 #TaoTeChing #道德经 #冥想 #东方哲学 #iPhoneApp #founder（按 2026 算法不靠 hashtag 排序，只作分类）"),
], col_widths=[3.5, 13.0])

doc.add_paragraph()

# ===== 6. pre-flight checklist =====
add_heading(doc, "6. 录前自查（避免 5s spinner 那种翻车）", level=1)
add_para(doc, "逐条对照录屏动作表，每条都要在 build 50 实机跑通再开录。", italic=True, size=10, color="6b6a63")
checks = [
    "PracticeView 顶部有 4 个 mood chip（build 50 新功能，build 49 没有）",
    "选 mood 后 verse 卡片 eyebrow 变红 + 显 TODAY'S VERSE · FOR YOU（不出现 spinner / loading）",
    "Library 经藏页有 3 个 hub 卡（不是 194 章老列表）",
    "道德经精讲 hub 卡有 PRO 角标",
    "精讲列表第 1 章可点进；第 8 章点进弹付费墙（不是直接锁死）",
    "JingjiangDetailView 6 段结构完整（原文/audio/通释/反常识点/scene/张力/行动）",
    "原文 detail 卡片有 Commentary + Reflection 两个 section",
    "SeekWisdomView 顶部有 scenario chip + Response Style（Free 锁定 Classic · Direct）",
    "「求」印章按钮存在（不是普通提交按钮）",
    "结果是 4 段（Passage/Wisdom/Reflection/Way Forward）+ 末尾 Pro banner",
    "付费墙有金色场景条（不是裸墙），3 条 hero + 6 条 feature 都在",
    "Pro 账户实跑时付费墙 plan 列表 = annual / lifetime / monthly（lifetime 排第一）",
    "iPhone 时区 = 中国时区，录屏时间显示正常（避免疑为海外汉化版）",
    "录屏 65s 总长不超 70s（超 70s 完播率掉一档）",
]
for c in checks:
    p = doc.add_paragraph()
    run = p.add_run("✓ " + c)
    run.font.size = Pt(10)
    run.font.name = "Microsoft YaHei"
    _yahei(run)
    run.font.color.rgb = RGBColor.from_string("2b2b26")

doc.add_paragraph()

# footer
foot = doc.add_paragraph()
foot.alignment = WD_ALIGN_PARAGRAPH.RIGHT
fr = foot.add_run("基于 iOS 源码核对 · 2026-09-06")
fr.font.size = Pt(9)
fr.font.italic = True
fr.font.color.rgb = RGBColor.from_string("9a9890")
_yahei(fr)

# save
out_path = r"C:\Users\Cyan\Desktop\TaoMind_TikTok_Video1_Script.docx"
doc.save(out_path)
print("Saved: " + out_path)
print("Size: " + str(os.path.getsize(out_path)) + " bytes")
