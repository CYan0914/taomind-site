# -*- coding: utf-8 -*-
"""TaoMind 官网博客生成器：读取 taomind-Streamlit 的 library_content.py（113 章），
生成双语 SEO 静态站（Tao Te Ching + Diamond Sutra 精讲），用于 GitHub Pages。

用法:  python generate_site.py
输出:  site/ 目录（index + 每章页面 + sitemap + robots + favicon）
"""
import html
import io
import os
import re
import shutil
import sys

LIBRARY_PATH = r"D:\projects\taomind-Streamlit\library_content.py"  # 保留兼容：实际走 LIB_DIR + SOURCE_FILES
ICON_PATH = r"C:\Users\Cyan\Desktop\TaoMind-iOS\Resources\Assets.xcassets\AppIcon.appiconset\AppIcon.png"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "site")
SITE_URL = "https://cyan0914.github.io/taomind-site/"

APP_NAME = "TaoMind"
APP_URL = "https://apps.apple.com/app/id6792008756"

LIB_DIR = r"D:\projects\taomind-Streamlit"

SOURCE_META = {
    "Tao Te Ching": {"slug": "tao-te-ching", "zh": "道德经", "zhUnit": "章", "title": "Tao Te Ching"},
    "Diamond Sutra": {"slug": "diamond-sutra", "zh": "金刚经", "zhUnit": "品", "title": "Diamond Sutra"},
    "太上感应篇": {"slug": "ganying", "zh": "太上感应篇", "zhUnit": "章", "title": "太上感应篇"},
    "清静经": {"slug": "qingjing", "zh": "清静经", "zhUnit": "章", "title": "清静经"},
    "列子": {"slug": "liezi", "zh": "列子", "zhUnit": "篇", "title": "列子"},
    "庄子": {"slug": "zhuangzi", "zh": "庄子", "zhUnit": "篇", "title": "庄子"},
}

# source -> (文件名, 变量名)。display_order 即文件内顺序，用作 URL 编号。
SOURCE_FILES = {
    "Tao Te Ching": ("library_content.py", "LIBRARY_CONTENT"),
    "Diamond Sutra": ("library_content.py", "LIBRARY_CONTENT"),
    "太上感应篇": ("library_ganying.py", "TAISHANG_GANYING"),
    "清静经": ("library_other.py", "LIBRARY_OTHER"),
    "列子": ("library_other.py", "LIBRARY_OTHER"),
    "庄子": ("library_zhuangzi.py", "LIBRARY_ZHUANGZI"),
}


def load_content():
    out = []
    cache = {}
    for source, (fname, var) in SOURCE_FILES.items():
        if fname not in cache:
            ns = {}
            src = io.open(os.path.join(LIB_DIR, fname), encoding="utf-8").read()
            exec(compile(src, fname, "exec"), ns)
            cache[fname] = ns
        for c in cache[fname][var]:
            if c.get("source") == source:
                out.append(c)
    return out


def entry_seq(c):
    """URL 与排序用的序号：display_order 在该 source 内的第几条（1-based）。
    感应篇/庄子等中文 chapter 名里没有数字，不能用 chapter_num。"""
    try:
        return int(c.get("display_order") or 0)
    except (TypeError, ValueError):
        return 0


def seq_list(source, content):
    items = [c for c in content if c.get("source") == source]
    items.sort(key=entry_seq)
    return items


def esc(t):
    return html.escape(t, quote=True)


def zh_label(source, chapter_num):
    m = SOURCE_META[source]
    return f"{m['zh']} 第{chapter_num}{m['zhUnit']}"


def slugify_source(source):
    return SOURCE_META[source]["slug"]


def chapter_num(chapter_str):
    m = re.search(r"(\d+)", chapter_str)
    return int(m.group(1)) if m else None


def render_commentary(text):
    """把 commentary 的 markdown-lite 转成 HTML：`**bold**` + `  \n` 换行。"""
    if not text:
        return ""
    # 转义后处理 bold
    t = esc(text)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    # `  \n` 换行 → 分段
    lines = t.split("\n")
    paras = [ln.strip() for ln in lines]
    paras = [p for p in paras if p]
    return "\n".join(f"<p>{p}</p>" for p in paras)


def teaser(text, max_chars=160):
    """精讲导读：截取 commentary 开头到句号边界的一两句话，作为免费预览。

    完整精讲是 App 的 Pro 卖点，网页只给一句导读引流下载，保护 App 付费墙。
    """
    if not text:
        return ""
    plain = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    plain = re.sub(r"  \n", " ", plain).replace("\n", " ")
    plain = " ".join(plain.split())
    if len(plain) <= max_chars:
        return esc(plain)
    cut = plain[:max_chars]
    # 在最近的句子边界（。！？.!)）处截断，避免半句
    m = re.search(r"[。！？.!?]", cut[::-1])
    end = max_chars - (m.start() + 1) if m else max_chars
    return esc(plain[:end].rstrip()) + "……"


def json_ld(page_title, description, canonical, date_published="2026-08-15"):
    return """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": %s,
  "description": %s,
  "publisher": {"@type": "Organization", "name": %s},
  "mainEntityOfPage": {"@type": "WebPage", "@id": %s}
}
</script>""" % (
        json_str(page_title),
        json_str(description),
        json_str(APP_NAME),
        json_str(canonical),
    )


def json_str(s):
    # simple JSON string escaping for the ld+json block
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def page_shell(title, description, canonical, body, og_image="", extra_head=""):
    og = ""
    if og_image:
        og = f'<meta property="og:image" content="{esc(og_image)}" />\n'
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<meta name="description" content="{desc}" />
<link rel="canonical" href="{canonical}" />
<meta property="og:type" content="article" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{desc}" />
<meta property="og:url" content="{canonical}" />
{og}<link rel="icon" href="{base}favicon.png" type="image/png" />
{jsonld}
<style>
:root {{ --ink:#2b2b26; --paper:#faf8f2; --muted:#6b6a63; --accent:#4a6b4a; --line:#e2ded2; }}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; padding:0; background:var(--paper); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif; line-height:1.65; }}
.container {{ max-width:760px; margin:0 auto; padding:2.5rem 1.5rem 4rem; }}
header.site {{ display:flex; align-items:baseline; justify-content:space-between; gap:1rem; flex-wrap:wrap; padding-bottom:1rem; border-bottom:1px solid var(--line); }}
.logo {{ font-size:1.1rem; font-weight:700; color:var(--ink); text-decoration:none; display:flex; align-items:center; gap:.5rem; }}
.logo img {{ width:26px; height:26px; border-radius:50%; }}
nav.top a {{ color:var(--accent); text-decoration:none; font-size:.9rem; margin-left:1rem; }}
.crumb {{ font-size:.85rem; color:var(--muted); margin:1.2rem 0 .2rem; }}
.crumb a {{ color:var(--muted); text-decoration:none; }}
h1 {{ font-size:2rem; line-height:1.25; margin:.4rem 0 .6rem; }}
.zh-tag {{ color:var(--muted); font-weight:400; font-size:1.05rem; }}
.verse {{ font-family:Georgia,'Times New Roman',serif; font-size:1.45rem; line-height:1.6; font-style:italic; color:#33302a; background:#f1ede1; border-left:4px solid var(--accent); padding:1.4rem 1.6rem; border-radius:0 8px 8px 0; margin:1.8rem 0; }}
h2 {{ font-size:1.15rem; margin:2rem 0 .5rem; color:var(--accent); letter-spacing:.02em; }}
.commentary p {{ margin:.5rem 0; }}
.reflect {{ background:#f1ede1; border-radius:8px; padding:1.2rem 1.4rem; font-style:italic; color:#44403a; }}
.pager {{ display:flex; justify-content:space-between; gap:1rem; margin-top:3rem; padding-top:1.2rem; border-top:1px solid var(--line); font-size:.9rem; }}
.pager a {{ color:var(--accent); text-decoration:none; max-width:45%; }}
.pager .next {{ text-align:right; }}
.cta {{ margin-top:3rem; text-align:center; background:#f1ede1; border-radius:10px; padding:1.6rem; }}
.cta a.btn {{ display:inline-block; background:var(--accent); color:#fff; text-decoration:none; padding:.7rem 1.6rem; border-radius:999px; font-weight:600; }}
.cta p {{ color:var(--muted); font-size:.9rem; margin:.6rem 0 0; }}
.list-group {{ margin:1.2rem 0; }}
.list-group h3 {{ font-size:1.05rem; margin:.6rem 0; color:var(--accent); }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); gap:.5rem; }}
.grid a {{ color:var(--ink); text-decoration:none; font-size:.92rem; padding:.35rem .6rem; border:1px solid var(--line); border-radius:6px; background:#fff; }}
.grid a:hover {{ border-color:var(--accent); color:var(--accent); }}
.hero {{ text-align:center; padding:1.5rem 0 1rem; }}
.hero h1 {{ font-size:2.3rem; }}
.hero p {{ color:var(--muted); max-width:560px; margin:.4rem auto 0; }}
footer.site {{ margin-top:3rem; padding-top:1.2rem; border-top:1px solid var(--line); color:var(--muted); font-size:.85rem; display:flex; justify-content:space-between; gap:1rem; flex-wrap:wrap; }}
</style>
</head>
<body>
{body}
</body>
</html>""".format(
        title=esc(title),
        desc=esc(description),
        canonical=esc(canonical),
        og=og,
        base=esc(BASE_REL),
        jsonld=json_ld(title, description, canonical),
        body=body,
    )


BASE_REL = ""


def chapter_url(source, num):
    return f"{slugify_source(source)}/chapter-{num}.html"


def chapter_canonical(source, num):
    return SITE_URL + chapter_url(source, num)


def build_chapter_page(c, prev_c=None, next_c=None, seq=0, total=0):
    source = c["source"]
    slug = slugify_source(source)
    meta = SOURCE_META[source]
    ch = c.get("chapter") or ""
    ch_en = c.get("chapter_en") or ""
    num = chapter_num(ch)
    seq_label = seq or num or 0

    is_en = source in ("Tao Te Ching", "Diamond Sutra")
    if is_en:
        zh = zh_label(source, num)
        title = f"{meta['title']} Chapter {num}: Full Text & Meaning | {APP_NAME}"
        description = (f"Read the original {meta['title']} Chapter {num} with a one-line insight. "
                       f"Get {APP_NAME} for the full plain-language commentary, reflection and daily practice. "
                       f"{(c.get('verse_text') or '')[:80]}")
        h1 = f"{meta['title']} Chapter {num} <span class=\"zh-tag\">· {esc(zh)}</span>"
        crumb_tail = f"Chapter {num}"
    else:
        # 中文经部（感应篇/清静经/列子/庄子）：chapter 名本身即标题
        title = f"{esc(ch)} · {meta['zh']}原文精讲 | {APP_NAME}"
        description = (f"{meta['zh']}{ch}原文 + 一句导读。"
                       f"完整白话精讲、反思与每日修习在 {APP_NAME} App。"
                       f"{(c.get('verse_text') or '')[:80]}")
        h1 = f"{esc(ch)} <span class=\"zh-tag\">· {esc(meta['zh'])}</span>"
        if ch_en:
            h1 += f"<br><span class=\"zh-tag\">{esc(ch_en)}</span>"
        crumb_tail = ch
    canonical = chapter_canonical(source, seq_label)

    prev_link, next_link = "", ""
    if prev_c:
        pn = entry_seq(prev_c)
        prev_link = f'<a href="chapter-{pn}.html">← {esc(prev_c.get("chapter") or "")}</a>'
    if next_c:
        nn = entry_seq(next_c)
        next_link = f'<a class="next" href="chapter-{nn}.html">{esc(next_c.get("chapter") or "")} →</a>'

    verse_html = esc(c.get("verse_text") or "")
    intro = teaser(c.get("commentary"))

    footer_total = f"All {total} chapters" if total else "All chapters"
    body = f"""<div class="container">
<header class="site">
  <a class="logo" href="{BASE_REL}index.html"><img src="{BASE_REL}favicon.png" alt="" />{APP_NAME}</a>
  <nav class="top"><a href="{BASE_REL}index.html">All Chapters</a><a href="{APP_URL}">Get the App</a></nav>
</header>
<p class="crumb"><a href="{BASE_REL}index.html">Home</a> › <a href="{BASE_REL}{slug}/index.html">{meta['title']}</a> › {esc(crumb_tail)}</p>
<h1>{h1}</h1>
<blockquote class="verse">{verse_html}</blockquote>
<h2>导读 · In brief</h2>
<p class="reflect">{intro}</p>
<div class="cta">
  <a class="btn" href="{APP_URL}">Read the full commentary in {APP_NAME} →</a>
  <p>The complete plain-language commentary, reflection and daily practice are in the {APP_NAME} app.</p>
</div>
<div class="pager">
  {prev_link}
  {next_link}
</div>
<footer class="site">
  <span>© 2026 {APP_NAME}</span>
  <span><a href="{BASE_REL}index.html">{footer_total}</a></span>
</footer>
</div>"""
    return page_shell(title, description, canonical, body)


def build_index(content):
    groups = {}
    for c in content:
        groups.setdefault(c["source"], []).append(c)

    total = sum(len(v) for v in groups.values())
    hero = f"""<div class="hero">
<h1>Daily Tao Te Ching &amp; Diamond Sutra — Read, Reflect, Grow</h1>
<h2 class="zh-hero">把《道德经》变成每天能用的一句话</h2>
<p>{total} chapters, each with the original verse and a one-line insight. Free to read on the web; get the app for the full plain-language commentary, reflection and daily practice.<br>写下你卡住的事，给你对症的那章经文、一段白话和今天就能做的一件事。</p>
</div>"""

    groups_html = []
    for source in SOURCE_META:
        items = seq_list(source, content)
        if not items:
            continue
        meta = SOURCE_META[source]
        links = []
        for c in items:
            seq = entry_seq(c)
            if source in ("Tao Te Ching", "Diamond Sutra"):
                label = f"{meta['title']} Chapter {chapter_num(c.get('chapter'))}"
            else:
                label = c.get("chapter") or f"{meta['zh']} {seq}"
            links.append(f'<a href="{chapter_url(source, seq)}">{esc(label)}</a>')
        groups_html.append(
            f'<div class="list-group"><h3>{esc(meta["title"])} · {esc(meta["zh"])} ({len(items)} {meta["zhUnit"]})</h3>'
            f'<div class="grid">{"".join(links)}</div></div>'
        )

    body = f"""<div class="container">
<header class="site">
  <a class="logo" href="{BASE_REL}index.html"><img src="{BASE_REL}favicon.png" alt="" />{APP_NAME}</a>
  <nav class="top"><a href="{APP_URL}">Get the App</a></nav>
</header>
{hero}
<div class="list-group"><h3>困住的时候 · When You Are Stuck</h3>
<p class="sub-pain">睡不着、焦虑、想辞职、失恋、拖延——每个具体处境，都有一章对得上。</p>
<div class="grid">
  <a href="{BASE_REL}problems/anxiety.html">焦虑</a><a href="{BASE_REL}problems/cant-sleep.html">睡不着</a><a href="{BASE_REL}problems/quit-job.html">想辞职</a><a href="{BASE_REL}problems/heartbreak.html">失恋</a><a href="{BASE_REL}problems/procrastination.html">拖延</a><a href="{BASE_REL}problems/burnout.html">撑不住</a><a href="{BASE_REL}problems/comparison.html">爱比较</a><a href="{BASE_REL}problems/index.html">全部 20 个 →</a>
</div></div>
{''.join(groups_html)}
<div class="cta">
  <a class="btn" href="{APP_URL}">Get one verse a day with {APP_NAME} →</a>
  <p>Daily Tao Te Ching verses, reflections and journaling.</p>
</div>
<footer class="site">
  <span>© 2026 {APP_NAME}</span>
  <span><a href="{BASE_REL}sitemap.xml">Sitemap</a></span>
</footer>
</div>"""
    return page_shell(
        f"{APP_NAME} — 道德经 / 金刚经 / 感应篇 / 庄子原文精讲 · Daily Wisdom, Verse by Verse",
        "道德经 81 章、金刚经 32 品、太上感应篇、庄子精选原文 + 一句导读，中英双语。完整白话精讲与每日修习在 TaoMind App。",
        SITE_URL,
        body,
    )


def build_source_index(source, items):
    meta = SOURCE_META[source]
    items = seq_list(source, items)
    links = []
    for c in items:
        seq = entry_seq(c)
        if source in ("Tao Te Ching", "Diamond Sutra"):
            label = f"{meta['title']} Chapter {chapter_num(c.get('chapter'))}"
        else:
            label = c.get("chapter") or f"{meta['zh']} {seq}"
        links.append(f'<a href="chapter-{seq}.html">{esc(label)}</a>')
    if source in ("Tao Te Ching", "Diamond Sutra"):
        h1 = f"{meta['title']} — All {len(items)} Chapters <span class=\"zh-tag\">· {esc(meta['zh'])}</span>"
    else:
        h1 = f"{esc(meta['zh'])} · 全 {len(items)} {meta['zhUnit']} <span class=\"zh-tag\">· {esc(meta['title'])}</span>"
    body = f"""<div class="container">
<header class="site">
  <a class="logo" href="{BASE_REL}index.html"><img src="{BASE_REL}favicon.png" alt="" />{APP_NAME}</a>
  <nav class="top"><a href="{BASE_REL}index.html">All Chapters</a><a href="{APP_URL}">Get the App</a></nav>
</header>
<p class="crumb"><a href="{BASE_REL}index.html">Home</a> › {meta['title']}</p>
<h1>{h1}</h1>
<div class="grid">{"".join(links)}</div>
<div class="cta">
  <a class="btn" href="{APP_URL}">Get one verse a day with {APP_NAME} →</a>
  <p>Daily Tao Te Ching verses, reflections and journaling.</p>
</div>
</div>"""
    return page_shell(
        f"{meta['zh']} · 全 {len(items)} {meta['zhUnit']}原文精讲 | {APP_NAME}",
        f"{meta['zh']}全 {len(items)} {meta['zhUnit']}原文 + 一句导读。完整白话精讲与每日修习在 TaoMind App。",
        SITE_URL + slugify_source(source) + "/",
        body,
    )


def build_problem_page(p, ttc_by_num, all_problems):
    """问题型落地页：用户搜的是处境，不是章号。

    结构：处境标题 → 共鸣 → 经文 → 老子怎么说 → 今天做一件事 → 下载。
    经文原文来自公共领域通行本；解读自写，不搬学者译文。
    """
    num = p["chapter"]
    entry = ttc_by_num.get(num) or {}
    verse = (entry.get("verse_text") or "").strip()
    ch_name = entry.get("chapter") or f"第{num}章"

    canonical = SITE_URL + f"problems/{p['slug']}.html"
    title = f"{p['h1']}｜道德经第{num}章怎么说 | {APP_NAME}"
    description = f"{p['pain']}《道德经》{ch_name}给的答案：{p['quote_note']}。"

    # 同类问题互链，提高站内爬取与停留
    others = [x for x in all_problems if x["slug"] != p["slug"]][:6]
    other_links = "".join(
        f'<a href="{x["slug"]}.html">{esc(x["h1"])}</a>' for x in others
    )

    body = f"""<div class="container">
<header class="site">
  <a class="logo" href="{BASE_REL}index.html"><img src="{BASE_REL}favicon.png" alt="" />{APP_NAME}</a>
  <nav class="top"><a href="{BASE_REL}index.html">All Chapters</a><a href="{APP_URL}">Get the App</a></nav>
</header>
<p class="crumb"><a href="{BASE_REL}index.html">Home</a> › 困住的时候</p>
<h1>{esc(p['h1'])}</h1>
<p class="sub-pain">{esc(p['pain'])}</p>
<blockquote class="verse">{esc(verse)}<span class="verse-src">——《道德经》{esc(ch_name)}</span></blockquote>
<h2>老子怎么说</h2>
<div class="commentary"><p>{esc(p['insight'])}</p></div>
<div class="keyline">{esc(p['quote_note'])}</div>
<h2>今天可以做的一件事</h2>
<div class="action-box">{esc(p['action'])}</div>
<div class="cta">
  <a class="btn" href="{APP_URL}">把这个方法装进手机 →</a>
  <p>{APP_NAME}：写下你的处境，给你对症的那一章，每天一句，连续打卡 7 天免费得 7 天 Pro。</p>
</div>
<div class="list-group">
  <h3>也许你还在困扰</h3>
  <div class="grid">{other_links}</div>
</div>
<footer class="site">
  <span>© 2026 {APP_NAME}</span>
  <span><a href="{BASE_REL}index.html">全部经文</a></span>
</footer>
</div>"""
    return page_shell(title, description, canonical, body)


def build_problems_index(problems):
    links = "".join(
        f'<a href="{p["slug"]}.html">{esc(p["h1"])}</a>' for p in problems
    )
    body = f"""<div class="container">
<header class="site">
  <a class="logo" href="{BASE_REL}index.html"><img src="{BASE_REL}favicon.png" alt="" />{APP_NAME}</a>
  <nav class="top"><a href="{BASE_REL}index.html">All Chapters</a><a href="{APP_URL}">Get the App</a></nav>
</header>
<p class="crumb"><a href="{BASE_REL}index.html">Home</a> › 困住的时候</p>
<h1>困住的时候，古人怎么说</h1>
<p class="sub-pain">睡不着、想辞职、放不下、怕失败——每一个具体处境，都有一章经文对得上。</p>
<div class="grid">{links}</div>
<div class="cta">
  <a class="btn" href="{APP_URL}">写下你的处境，让 {APP_NAME} 给你找那一章 →</a>
  <p>道德经 81 章 + 金刚经 32 品，中英双语，每日一签。</p>
</div>
</div>"""
    return page_shell(
        f"困住的时候，古人怎么说 | {APP_NAME}",
        "睡不着、焦虑、想辞职、失恋、拖延、职场压力——每个具体处境对应一章《道德经》，原文 + 一句解读 + 今天能做的一件事。",
        SITE_URL + "problems/",
        body,
    )


def main():
    content = load_content()
    from problems_data import PROBLEMS
    try:
        if os.path.isdir(OUT_DIR):
            shutil.rmtree(OUT_DIR)
    except OSError:
        # Windows 文件锁（浏览器仍持有句柄）：降级为覆盖写入
        pass
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUT_DIR, "tao-te-ching"), exist_ok=True)
    os.makedirs(os.path.join(OUT_DIR, "diamond-sutra"), exist_ok=True)

    # index
    with io.open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_index(content))

    # per-source ordering for prev/next: display_order 在该 source 内的顺序
    by_source = {}
    for c in content:
        by_source.setdefault(c["source"], []).append(c)
    for source, items in by_source.items():
        items.sort(key=entry_seq)

    urls = []

    for source, items in by_source.items():
        sub = os.path.join(OUT_DIR, slugify_source(source))
        os.makedirs(sub, exist_ok=True)
        with io.open(os.path.join(sub, "index.html"), "w", encoding="utf-8") as f:
            f.write(build_source_index(source, items))
        urls.append(SITE_URL + slugify_source(source) + "/")

        # 该 source 内第几条（1-based）就是 URL 编号，保证同一 source 内唯一连续
        for idx, c in enumerate(items):
            seq = idx + 1
            fn = os.path.join(sub, f"chapter-{seq}.html")
            prev_c = items[idx - 1] if idx > 0 else None
            next_c = items[idx + 1] if idx < len(items) - 1 else None
            html_page = build_chapter_page(c, prev_c, next_c, seq=seq, total=len(items))
            with io.open(fn, "w", encoding="utf-8") as f:
                f.write(html_page)
            urls.append(chapter_canonical(source, seq))

    # 问题型落地页：/problems/
    ttc_by_num = {
        int(c.get("display_order") or 0): c
        for c in content if c.get("source") == "Tao Te Ching"
    }
    prob_dir = os.path.join(OUT_DIR, "problems")
    os.makedirs(prob_dir, exist_ok=True)
    with io.open(os.path.join(prob_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_problems_index(PROBLEMS))
    urls.append(SITE_URL + "problems/")
    for p in PROBLEMS:
        with io.open(os.path.join(prob_dir, p["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(build_problem_page(p, ttc_by_num, PROBLEMS))
        urls.append(SITE_URL + "problems/" + p["slug"] + ".html")

    # sitemap
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
               f"  <url><loc>{SITE_URL}</loc></url>"]
    for u in sorted(set(urls)):
        sitemap.append(f"  <url><loc>{u}</loc></url>")
    sitemap.append("</urlset>")
    with io.open(os.path.join(OUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sitemap))

    # robots
    with io.open(os.path.join(OUT_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n\nSitemap: " + SITE_URL + "sitemap.xml\n")

    # favicon（缩小到 64x64，避免 860KB 原图）
    if os.path.isfile(ICON_PATH):
        try:
            from PIL import Image
            im = Image.open(ICON_PATH).convert("RGB")
            im.thumbnail((64, 64))
            im.save(os.path.join(OUT_DIR, "favicon.png"))
        except Exception:
            shutil.copy2(ICON_PATH, os.path.join(OUT_DIR, "favicon.png"))

    # .nojekyll for GitHub Pages
    with io.open(os.path.join(OUT_DIR, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")

    print(f"Generated {len(content)} chapter pages + index + sitemap in {OUT_DIR}")


if __name__ == "__main__":
    main()
