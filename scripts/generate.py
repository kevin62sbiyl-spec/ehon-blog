#!/usr/bin/env python3
"""
絵本×教養ブログ 自動生成システム
使い方: python scripts/generate.py "テーマ名"
例:    python scripts/generate.py "ももたろうから学ぶチームの作り方"
"""

import anthropic
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# ── 設定 ──────────────────────────────────────────
BASE_DIR   = Path(__file__).parent.parent
POSTS_DIR  = BASE_DIR / "posts"
DOCS_DIR   = BASE_DIR / "docs"
POSTS_OUT  = DOCS_DIR / "posts"
client     = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

SITE_CONFIG = {
    "title":       "絵本の教室｜教養×絵本×子育て×社会人",
    "description": "絵本の名作から、仕事・子育て・人生に使える教養を届けるブログ",
    "url":         "https://yourusername.github.io/ehon-blog",
    "author":      "絵本の教室",
    "youtube_channel": "https://www.youtube.com/@your-channel",
}

# ── AIでコンテンツ生成 ────────────────────────────
def generate_content(theme: str) -> dict:
    print(f"\n📚 AI組織起動中... テーマ:「{theme}」\n")

    system = """あなたは「教養×絵本×子育て×社会人」ブログの専門家AIチームです。
テーマを受け取り、以下のJSON形式のみで返してください（前置き・コードブロック不要）。

{
  "slug": "url用スラッグ（英小文字・ハイフン区切り・20文字以内）",
  "title": "SEOタイトル（30文字前後）",
  "description": "メタディスクリプション（120文字前後）",
  "keywords": ["KW1","KW2","KW3","KW4","KW5"],
  "category": "カテゴリ名（例：リーダーシップ）",
  "tags": ["タグ1","タグ2","タグ3"],
  "reading_time": 8,
  "intro": "導入文（250文字。読者の悩みから始める）",
  "sections": [
    {
      "h2": "セクション見出し",
      "body": "本文（400文字程度。具体例・エピソードを含む）",
      "h3s": [
        {"h3": "小見出し", "body": "小見出し本文（200文字）"}
      ]
    }
  ],
  "conclusion": "まとめ（200文字。行動を促す締めで終える）",
  "youtube": {
    "hook": "YouTube冒頭フック台本（100文字）",
    "title_ideas": ["タイトル案1","タイトル案2","タイトル案3"],
    "cta_text": "動画への誘導テキスト（50文字）"
  },
  "affiliate": [
    {"name": "商品名", "description": "なぜおすすめか（50文字）", "search_keyword": "Amazon検索KW"}
  ],
  "related_themes": ["関連テーマ1","関連テーマ2","関連テーマ3"]
}

sectionsは5つ作成してください。各bodyは必ず400文字以上。"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=6000,
        system=system,
        messages=[{"role": "user", "content": f"テーマ：「{theme}」\n\nこのテーマで全コンテンツを生成してください。"}]
    )

    text = message.content[0].text
    clean = re.sub(r"```json|```", "", text).strip()
    return json.loads(clean)


# ── Markdown保存 ──────────────────────────────────
def save_markdown(theme: str, data: dict, date_str: str) -> Path:
    slug = data.get("slug", re.sub(r"[^\w]", "-", theme)[:30])
    filename = f"{date_str}-{slug}.md"
    path = POSTS_DIR / filename

    tags_str  = ", ".join(data.get("tags", []))
    kw_str    = ", ".join(data.get("keywords", []))
    affiliate_md = "\n".join([
        f"- **{a['name']}**：{a['description']}（Amazon検索：`{a['search_keyword']}`）"
        for a in data.get("affiliate", [])
    ])
    related_md = "\n".join([f"- {t}" for t in data.get("related_themes", [])])
    yt = data.get("youtube", {})
    yt_titles = "\n".join([f"{i+1}. {t}" for i, t in enumerate(yt.get("title_ideas", []))])

    sections_md = ""
    for sec in data.get("sections", []):
        sections_md += f"\n## {sec['h2']}\n\n{sec['body']}\n"
        for h3 in sec.get("h3s", []):
            sections_md += f"\n### {h3['h3']}\n\n{h3['body']}\n"

    content = f"""---
title: "{data['title']}"
description: "{data['description']}"
date: "{date_str}"
slug: "{slug}"
category: "{data.get('category', '教養')}"
tags: [{tags_str}]
keywords: [{kw_str}]
reading_time: {data.get('reading_time', 8)}
youtube_hook: "{yt.get('hook', '')}"
youtube_titles: |
{chr(10).join('  ' + t for t in yt.get('title_ideas', []))}
---

{data['intro']}

{sections_md}

## まとめ

{data['conclusion']}

---

## 📺 YouTube動画でも解説しています

{yt.get('cta_text', 'この内容を動画でわかりやすく解説しています。')}

▶ チャンネルはこちら → [{SITE_CONFIG['youtube_channel']}]({SITE_CONFIG['youtube_channel']})

**動画タイトル案：**
{yt_titles}

---

## 📚 この記事に関連するおすすめ本

{affiliate_md}

---

## 関連テーマ

{related_md}
"""
    path.write_text(content, encoding="utf-8")
    print(f"  ✅ Markdown保存: posts/{filename}")
    return path


# ── HTML記事ページ生成 ────────────────────────────
def generate_article_html(data: dict, date_str: str, all_posts: list) -> tuple[str, str]:
    slug      = data["slug"]
    title     = data["title"]
    desc      = data["description"]
    keywords  = ", ".join(data.get("keywords", []))
    site_url  = SITE_CONFIG["url"]
    site_title= SITE_CONFIG["title"]
    yt_ch     = SITE_CONFIG["youtube_channel"]

    tags_html = "".join([f'<span class="tag">{t}</span>' for t in data.get("tags", [])])
    yt        = data.get("youtube", {})
    yt_titles = "".join([f"<li>{t}</li>" for t in yt.get("title_ideas", [])])
    affiliate_html = "".join([
        f'<div class="affiliate-item"><strong>{a["name"]}</strong><p>{a["description"]}</p>'
        f'<a href="https://www.amazon.co.jp/s?k={a["search_keyword"].replace(" ","+")}" '
        f'target="_blank" rel="noopener nofollow" class="amazon-btn">Amazonで見る →</a></div>'
        for a in data.get("affiliate", [])
    ])

    # 目次
    toc_items = "".join([
        f'<li><a href="#section-{i}">{sec["h2"]}</a></li>'
        for i, sec in enumerate(data.get("sections", []))
    ])

    # 本文
    body_html = f'<p class="intro">{data["intro"]}</p>'
    for i, sec in enumerate(data.get("sections", [])):
        body_html += f'<h2 id="section-{i}">{sec["h2"]}</h2>\n<p>{sec["body"]}</p>\n'
        for h3 in sec.get("h3s", []):
            body_html += f'<h3>{h3["h3"]}</h3>\n<p>{h3["body"]}</p>\n'

    # 関連記事（最新3件、自分以外）
    others = [p for p in all_posts if p.get("slug") != slug][:3]
    related_html = "".join([
        f'<a class="related-card" href="{site_url}/posts/{p["slug"]}.html">'
        f'<span class="related-cat">{p.get("category","教養")}</span>'
        f'<span class="related-title">{p["title"]}</span></a>'
        for p in others
    ])

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | {site_title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{keywords}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{site_url}/posts/{slug}.html">
<link rel="canonical" href="{site_url}/posts/{slug}.html">
<link rel="stylesheet" href="../assets/css/style.css">
<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"BlogPosting",
  "headline":"{title}",
  "description":"{desc}",
  "datePublished":"{date_str}",
  "author":{{"@type":"Person","name":"{SITE_CONFIG['author']}"}},
  "publisher":{{"@type":"Organization","name":"{site_title}"}}
}}
</script>
</head>
<body>
<header class="site-header">
  <div class="container">
    <a class="logo" href="../index.html">📚 {SITE_CONFIG['author']}</a>
    <nav><a href="../index.html">ホーム</a><a href="{yt_ch}" target="_blank" rel="noopener">YouTube</a></nav>
  </div>
</header>

<main class="article-layout container">
  <article class="article-body">
    <div class="article-meta">
      <span class="category-badge">{data.get('category','教養')}</span>
      <time datetime="{date_str}">{date_str}</time>
      <span class="reading-time">約{data.get('reading_time',8)}分</span>
    </div>
    <h1 class="article-title">{title}</h1>
    <div class="tags">{tags_html}</div>

    <nav class="toc">
      <p class="toc-title">目次</p>
      <ol>{toc_items}</ol>
    </nav>

    <div class="article-content">
      {body_html}
    </div>

    <div class="conclusion-box">
      <h2>まとめ</h2>
      <p>{data['conclusion']}</p>
    </div>

    <div class="youtube-cta">
      <div class="yt-icon">▶</div>
      <div>
        <p class="yt-label">YouTube動画でも解説しています</p>
        <p class="yt-hook">{yt.get('hook','この内容を動画でわかりやすく解説しています。')}</p>
        <a href="{yt_ch}" target="_blank" rel="noopener" class="yt-btn">チャンネルを見る →</a>
      </div>
    </div>

    <div class="youtube-titles">
      <p class="section-label">🎬 動画タイトル候補</p>
      <ol>{yt_titles}</ol>
    </div>

    <div class="affiliate-section">
      <p class="section-label">📚 おすすめ関連書籍</p>
      {affiliate_html}
    </div>
  </article>

  <aside class="sidebar">
    <div class="sidebar-widget">
      <p class="widget-title">📺 YouTubeチャンネル</p>
      <p style="font-size:13px;line-height:1.6;margin-bottom:12px">絵本から学ぶビジネス・子育て教養を毎週配信中</p>
      <a href="{yt_ch}" target="_blank" rel="noopener" class="yt-btn" style="display:block;text-align:center">チャンネル登録 →</a>
    </div>
    <div class="sidebar-widget">
      <p class="widget-title">🔗 関連記事</p>
      <div class="related-cards">{related_html if related_html else '<p style="font-size:13px;color:#888">記事を追加すると表示されます</p>'}</div>
    </div>
  </aside>
</main>

<footer class="site-footer">
  <div class="container">
    <p>© 2025 {SITE_CONFIG['author']} | <a href="{yt_ch}" target="_blank" rel="noopener">YouTube</a></p>
  </div>
</footer>
<script src="../assets/js/main.js"></script>
</body>
</html>"""
    return slug, html


# ── トップページ生成 ──────────────────────────────
def generate_index_html(all_posts: list) -> str:
    site_title = SITE_CONFIG["title"]
    site_desc  = SITE_CONFIG["description"]
    site_url   = SITE_CONFIG["url"]
    yt_ch      = SITE_CONFIG["youtube_channel"]

    cards = "".join([
        f'''<a class="post-card" href="{site_url}/posts/{p['slug']}.html">
          <div class="card-meta">
            <span class="category-badge">{p.get('category','教養')}</span>
            <time>{p.get('date','')}</time>
          </div>
          <h2 class="card-title">{p['title']}</h2>
          <p class="card-desc">{p['description']}</p>
          <div class="card-tags">{''.join(f'<span class="tag">{t}</span>' for t in p.get('tags',[])[:3])}</div>
          <span class="card-reading">約{p.get('reading_time',8)}分</span>
        </a>'''
        for p in all_posts
    ])

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{site_title}</title>
<meta name="description" content="{site_desc}">
<meta property="og:title" content="{site_title}">
<meta property="og:description" content="{site_desc}">
<link rel="canonical" href="{site_url}/">
<link rel="stylesheet" href="assets/css/style.css">
<script type="application/ld+json">
{{
  "@context":"https://schema.org",
  "@type":"Blog",
  "name":"{site_title}",
  "description":"{site_desc}",
  "url":"{site_url}"
}}
</script>
</head>
<body>
<header class="site-header">
  <div class="container">
    <a class="logo" href="index.html">📚 {SITE_CONFIG['author']}</a>
    <nav><a href="index.html">ホーム</a><a href="{yt_ch}" target="_blank" rel="noopener">YouTube</a></nav>
  </div>
</header>

<div class="hero">
  <div class="container">
    <p class="hero-eyebrow">教養 × 絵本 × 子育て × 社会人</p>
    <h1 class="hero-title">絵本が教えてくれた、<br>大人のための知恵</h1>
    <p class="hero-sub">{site_desc}</p>
    <a href="{yt_ch}" target="_blank" rel="noopener" class="hero-yt-btn">▶ YouTubeでも発信中</a>
  </div>
</div>

<main class="container">
  <p class="section-heading">最新記事</p>
  <div class="posts-grid">
    {cards if cards else '<p style="text-align:center;color:#888;padding:3rem">まだ記事がありません。generate.pyを実行して記事を追加してください。</p>'}
  </div>
</main>

<footer class="site-footer">
  <div class="container">
    <p>© 2025 {SITE_CONFIG['author']} | <a href="{yt_ch}" target="_blank" rel="noopener">YouTube</a></p>
  </div>
</footer>
<script src="assets/js/main.js"></script>
</body>
</html>"""


# ── 全投稿データ読み込み ──────────────────────────
def load_all_posts() -> list:
    posts = []
    for f in sorted(POSTS_DIR.glob("*.md"), reverse=True):
        meta = {}
        lines = f.read_text(encoding="utf-8").split("\n")
        in_fm = False
        for line in lines:
            if line.strip() == "---":
                in_fm = not in_fm
                continue
            if in_fm:
                if ":" in line:
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip().strip('"')
        if meta.get("title"):
            meta.setdefault("tags", [])
            posts.append(meta)
    return posts


# ── サイト全体ビルド ──────────────────────────────
def build_site(new_data: dict = None, date_str: str = None):
    print("  🔨 サイトをビルド中...")
    POSTS_OUT.mkdir(parents=True, exist_ok=True)

    all_posts = load_all_posts()

    # 記事HTML生成
    for f in sorted(POSTS_DIR.glob("*.md"), reverse=True):
        lines  = f.read_text(encoding="utf-8").split("\n")
        meta   = {}
        in_fm  = False
        for line in lines:
            if line.strip() == "---":
                in_fm = not in_fm; continue
            if in_fm and ":" in line:
                k, _, v = line.partition(":")
                meta[k.strip()] = v.strip().strip('"')
        if not meta.get("slug"):
            continue
        # 最新データがあればそれを優先
        if new_data and meta.get("slug") == new_data.get("slug"):
            data_to_use = new_data
        else:
            data_to_use = {
                "slug": meta.get("slug",""),
                "title": meta.get("title",""),
                "description": meta.get("description",""),
                "category": meta.get("category","教養"),
                "tags": [t.strip() for t in meta.get("tags","").split(",") if t.strip()],
                "keywords": [],
                "reading_time": int(meta.get("reading_time",8)),
                "intro": "",
                "sections": [],
                "conclusion": "",
                "youtube": {"hook":"","title_ideas":[],"cta_text":""},
                "affiliate": [],
            }
        slug, html = generate_article_html(data_to_use, meta.get("date", date_str or ""), all_posts)
        out_path = POSTS_OUT / f"{slug}.html"
        out_path.write_text(html, encoding="utf-8")

    # トップページ
    index_html = generate_index_html(all_posts)
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print("  ✅ index.html 更新完了")
    print(f"  ✅ 記事ページ {len(all_posts)} 件 生成完了")


# ── メイン ────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print("使い方: python scripts/generate.py \"テーマ名\"")
        print("例:    python scripts/generate.py \"ももたろうから学ぶチームの作り方\"")
        sys.exit(1)

    theme    = sys.argv[1]
    date_str = datetime.now().strftime("%Y-%m-%d")

    print("=" * 55)
    print("  📚 絵本×教養ブログ 自動生成システム")
    print("=" * 55)

    # 1. AIでコンテンツ生成
    data = generate_content(theme)
    print(f"  ✅ コンテンツ生成完了: {data['title']}")

    # 2. Markdown保存
    save_markdown(theme, data, date_str)

    # 3. サイトビルド
    build_site(new_data=data, date_str=date_str)

    print("\n" + "=" * 55)
    print("  🎉 完了！")
    print(f"  📄 タイトル : {data['title']}")
    print(f"  🔗 URL候補  : /posts/{data['slug']}.html")
    print(f"  📁 出力先   : docs/")
    print("\n  次のステップ:")
    print("  1. git add . && git commit -m 'add: 新記事' && git push")
    print("  2. GitHub Pages で自動公開されます")
    print("=" * 55)


if __name__ == "__main__":
    main()
