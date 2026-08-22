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

LIBRARY_PATH = r"D:\projects\taomind-Streamlit\library_content.py"
ICON_PATH = r"C:\Users\Cyan\Desktop\TaoMind-iOS\Resources\Assets.xcassets\AppIcon.appiconset\AppIcon.png"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "site")
SITE_URL = "https://cyan0914.github.io/taomind-site/"

APP_NAME = "TaoMind"
APP_URL = "https://apps.apple.com/app/id6800654302"

SOURCE_META = {
    "Tao Te Ching": {"slug": "tao-te-ching", "zh": "道德经", "zhUnit": "章", "title": "Tao Te Ching"},
    "Diamond Sutra": {"slug": "diamond-sutra", "zh": "金刚经", "zhUnit": "品", "title": "Diamond Sutra"},
}


def load_content():
    ns = {}
    src = io.open(LIBRARY_PATH, encoding="utf-8").read()
    exec(compile(src, "library_content.py", "exec"), ns)
    return ns["LIBRARY_CONTENT"]


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


def build_chapter_page(c, prev_c=None, next_c=None):
    source = c["source"]
    num = chapter_num(c["chapter"])
    slug = slugify_source(source)
    meta = SOURCE_META[source]
    zh = zh_label(source, num)

    title = f"{meta['title']} Chapter {num}: Full Text & Meaning | {APP_NAME}"
    verse_first = c["verse_text"]
    description = (f"Read the original {meta['title']} Chapter {num} with a one-line insight. "
                   f"Get {APP_NAME} for the full plain-language commentary, reflection and daily practice. "
                   f"{verse_first[:80]}")
    canonical = chapter_canonical(source, num)

    prev_link, next_link = "", ""
    if prev_c:
        pn = chapter_num(prev_c["chapter"])
        prev_link = f'<a href="chapter-{pn}.html">← {esc(prev_c["chapter"])}</a>'
    if next_c:
        nn = chapter_num(next_c["chapter"])
        next_link = f'<a class="next" href="chapter-{nn}.html">{esc(next_c["chapter"])} →</a>'

    verse_html = esc(c["verse_text"])
    intro = teaser(c["commentary"])

    body = f"""<div class="container">
<header class="site">
  <a class="logo" href="{BASE_REL}index.html"><img src="{BASE_REL}favicon.png" alt="" />{APP_NAME}</a>
  <nav class="top"><a href="{BASE_REL}index.html">All Chapters</a><a href="{APP_URL}">Get the App</a></nav>
</header>
<p class="crumb"><a href="{BASE_REL}index.html">Home</a> › <a href="{BASE_REL}{slug}/index.html">{meta['title']}</a> › Chapter {num}</p>
<h1>{meta['title']} Chapter {num} <span class="zh-tag">· {esc(zh)}</span></h1>
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
  <span><a href="{BASE_REL}index.html">All 113 chapters</a></span>
</footer>
</div>"""
    return page_shell(title, description, canonical, body)


def build_index(content):
    groups = {}
    for c in content:
        groups.setdefault(c["source"], []).append(c)

    hero = """<div class="hero">
<h1>Daily Tao Te Ching &amp; Diamond Sutra — Read, Reflect, Grow</h1>
<p>113 chapters, each with the original verse and a one-line insight. Free to read on the web; get the app for the full plain-language commentary, reflection and daily practice.</p>
</div>"""

    groups_html = []
    for source in ["Tao Te Ching", "Diamond Sutra"]:
        items = groups.get(source, [])
        items.sort(key=lambda c: chapter_num(c["chapter"]) or 0)
        meta = SOURCE_META[source]
        links = []
        for c in items:
            num = chapter_num(c["chapter"])
            links.append(f'<a href="{chapter_url(source, num)}">{meta["title"]} Chapter {num}</a>')
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
        f"{APP_NAME} — Daily Tao Te Ching & Diamond Sutra, Verse by Verse",
        "Read all 81 chapters of the Tao Te Ching and 32 sections of the Diamond Sutra. Get the TaoMind app for the full plain-language commentary and daily practice.",
        SITE_URL,
        body,
    )


def build_source_index(source, items):
    meta = SOURCE_META[source]
    items.sort(key=lambda c: chapter_num(c["chapter"]) or 0)
    links = []
    for c in items:
        num = chapter_num(c["chapter"])
        links.append(f'<a href="chapter-{num}.html">{meta["title"]} Chapter {num}</a>')
    body = f"""<div class="container">
<header class="site">
  <a class="logo" href="{BASE_REL}index.html"><img src="{BASE_REL}favicon.png" alt="" />{APP_NAME}</a>
  <nav class="top"><a href="{BASE_REL}index.html">All Chapters</a><a href="{APP_URL}">Get the App</a></nav>
</header>
<p class="crumb"><a href="{BASE_REL}index.html">Home</a> › {meta['title']}</p>
<h1>{meta['title']} — All {len(items)} Chapters <span class="zh-tag">· {esc(meta['zh'])}</span></h1>
<div class="grid">{"".join(links)}</div>
<div class="cta">
  <a class="btn" href="{APP_URL}">Get one verse a day with {APP_NAME} →</a>
  <p>Daily Tao Te Ching verses, reflections and journaling.</p>
</div>
</div>"""
    return page_shell(
        f"{meta['title']} — All {len(items)} Chapters | {APP_NAME}",
        f"Read all {len(items)} chapters of the {meta['title']} ({meta['zh']}). Get the TaoMind app for the full plain-language commentary and daily practice.",
        SITE_URL + slugify_source(source) + "/",
        body,
    )


def main():
    content = load_content()
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

    # per-source ordering for prev/next (natural chapter order)
    by_source = {}
    for c in content:
        by_source.setdefault(c["source"], []).append(c)
    for source, items in by_source.items():
        items.sort(key=lambda c: chapter_num(c["chapter"]) or 0)

    urls = []

    for source, items in by_source.items():
        sub = os.path.join(OUT_DIR, slugify_source(source))
        os.makedirs(sub, exist_ok=True)
        with io.open(os.path.join(sub, "index.html"), "w", encoding="utf-8") as f:
            f.write(build_source_index(source, items))
        urls.append(SITE_URL + slugify_source(source) + "/")

        for c in items:
            num = chapter_num(c["chapter"])
            fn = os.path.join(sub, f"chapter-{num}.html")
            idx = items.index(c)
            prev_c = items[idx - 1] if idx > 0 else None
            next_c = items[idx + 1] if idx < len(items) - 1 else None
            html_page = build_chapter_page(c, prev_c, next_c)
            with io.open(fn, "w", encoding="utf-8") as f:
                f.write(html_page)
            urls.append(chapter_canonical(source, num))

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
