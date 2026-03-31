#!/usr/bin/env python3
"""
カテゴリページ生成スクリプト
使い方: python scripts/build_categories.py
"""

import re
from pathlib import Path

BASE_DIR  = Path(__file__).parent.parent
POSTS_DIR = BASE_DIR / "posts"
DOCS_DIR  = BASE_DIR / "docs"

SITE_CONFIG = {
    "title":       "教養の教室｜社会人のための知的生活マガジン",
    "url":         "https://kevin62sbiyl-spec.github.io/ehon-blog",
    "author":      "教養の教室",
    "youtube_channel": "https://www.youtube.com/@your-channel",
}

CATEGORY_DESC = {
    "お金と資本":  "資本主義・投資・経済の仕組みを基礎から理解する",
    "宗教":        "世界の主要宗教と信仰の本質を知る",
    "哲学・思想":  "古代から現代まで、人類の思索の歴史をたどる",
    "歴史":        "世界史の大きな流れから現代を読み解く",
    "芸術":        "美術・音楽・建築・映画、表現の本質に迫る",
    "言葉と文学":  "言語・文学・思想、言葉の力を深く知る",
}

CATEGORY_ICONS = {
    "お金と資本":  "💰",
    "宗教":        "🕊",
    "哲学・思想":  "🤔",
    "歴史":        "📜",
    "芸術":        "🎨",
    "言葉と文学":  "📖",
}


def load_all_posts():
    posts = []
    for f in sorted(POSTS_DIR.glob("*.md"), reverse=True):
        meta, in_fm = {}, False
        for line in f.read_text(encoding="utf-8").split("\n"):
            if line.strip() == "---":
                in_fm = not in_fm; continue
            if in_fm and ":" in line:
                k, _, v = line.partition(":")
                meta[k.strip()] = v.strip().strip('"')
        if meta.get("title"):
            raw = meta.get("tags", "")
            meta["tags"] = [t.strip().strip("[]") for t in raw.split(",") if t.strip()]
            posts.append(meta)
    return posts


def build_categories():
    all_posts = load_all_posts()
    site_url  = SITE_CONFIG["url"]
    yt_ch     = SITE_CONFIG["youtube_channel"]

    # カテゴリ別に分類
    by_cat = {}
    for p in all_posts:
        cat = p.get("category", "その他")
        by_cat.setdefault(cat, []).append(p)

    # カテゴリ一覧ナビ
    cat_nav = "".join([
        f'<a href="#{cat}" class="cat-nav-item">'
        f'<span class="cat-nav-icon">{CATEGORY_ICONS.get(cat,"📚")}</span>'
        f'<span>{cat}</span>'
        f'<span class="cat-nav-count">{len(posts)}本</span>'
        f'</a>'
        for cat, posts in by_cat.items()
    ])

    # 各カテゴリセクション
    sections_html = ""
    for cat, posts in by_cat.items():
        icon = CATEGORY_ICONS.get(cat, "📚")
        desc = CATEGORY_DESC.get(cat, "")
        cards = "".join([
            f'<a class="post-card" href="{site_url}/posts/{p["slug"]}.html">'
            f'<div class="card-meta"><time>{p.get("date","")}</time><span class="reading-time">約{p.get("reading_time",10)}分</span></div>'
            f'<h3 class="card-title">{p["title"]}</h3>'
            f'<p class="card-desc">{p["description"]}</p>'
            f'<div class="card-tags">{"".join(f"<span class=\'tag\'>{t}</span>" for t in p.get("tags",[])[:3])}</div>'
            f'</a>'
            for p in posts
        ])
        sections_html += f'''
<section class="cat-section" id="{cat}">
  <div class="cat-header">
    <span class="cat-icon">{icon}</span>
    <div>
      <h2 class="cat-title">{cat}</h2>
      <p class="cat-desc">{desc}</p>
    </div>
    <span class="cat-count">{len(posts)}記事</span>
  </div>
  <div class="posts-grid">{cards}</div>
</section>'''

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>カテゴリ一覧 | {SITE_CONFIG['title']}</title>
<meta name="description" content="お金と資本・宗教・哲学・歴史・芸術・言葉と文学。6つの教養カテゴリから記事を探せます。">
<link rel="canonical" href="{site_url}/categories.html">
<link rel="stylesheet" href="assets/css/style.css">
<style>
.cat-nav {{ display:flex;flex-wrap:wrap;gap:10px;margin:32px 0 48px; }}
.cat-nav-item {{ display:flex;align-items:center;gap:8px;padding:12px 18px;background:#fff;border:1px solid var(--border);border-radius:var(--r-lg);font-size:14px;color:var(--ink-soft);transition:all .2s;text-decoration:none; }}
.cat-nav-item:hover {{ background:var(--accent-lt);color:var(--accent);border-color:var(--accent); }}
.cat-nav-icon {{ font-size:18px; }}
.cat-nav-count {{ font-size:12px;color:var(--ink-muted);margin-left:4px; }}
.cat-section {{ margin-bottom:64px; }}
.cat-header {{ display:flex;align-items:center;gap:16px;margin-bottom:24px;padding-bottom:16px;border-bottom:2px solid var(--ink); }}
.cat-icon {{ font-size:32px;flex-shrink:0; }}
.cat-title {{ font-family:var(--serif);font-size:22px;font-weight:700;margin-bottom:4px; }}
.cat-desc {{ font-size:13px;color:var(--ink-soft); }}
.cat-count {{ margin-left:auto;font-size:13px;color:var(--ink-muted);white-space:nowrap; }}
</style>
</head>
<body>
<header class="site-header">
  <div class="container">
    <a class="logo" href="index.html">{SITE_CONFIG['author']}</a>
    <nav>
      <a href="index.html">ホーム</a>
      <a href="categories.html">カテゴリ</a>
      <a href="{yt_ch}" target="_blank" rel="noopener">YouTube</a>
    </nav>
  </div>
</header>

<div class="hero" style="padding:48px 0">
  <div class="container">
    <p class="hero-eyebrow">6つの教養テーマ</p>
    <h1 class="hero-title" style="font-size:clamp(24px,4vw,38px)">カテゴリから記事を探す</h1>
  </div>
</div>

<main class="container">
  <nav class="cat-nav">{cat_nav}</nav>
  {sections_html}
</main>

<footer class="site-footer">
  <div class="container"><p>© 2025 {SITE_CONFIG['author']} | <a href="{yt_ch}" target="_blank" rel="noopener">YouTube</a></p></div>
</footer>
<script src="assets/js/main.js"></script>
</body>
</html>"""

    out = DOCS_DIR / "categories.html"
    out.write_text(html, encoding="utf-8")
    total = sum(len(v) for v in by_cat.values())
    print(f"✅ categories.html 生成完了（{len(by_cat)}カテゴリ・{total}記事）")
    print(f"\n反映するには:")
    print(f"  git add . && git commit -m 'add: カテゴリページ' && git push")


if __name__ == "__main__":
    build_categories()
