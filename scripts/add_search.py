#!/usr/bin/env python3
"""
サイト内検索機能を追加するスクリプト
- トップページに検索窓を追加
- 全記事データをsearch.jsonとして出力
- 検索UIをsearch.htmlとして生成
"""

from pathlib import Path
import json, re

BASE_DIR  = Path(".")
DOCS_DIR  = BASE_DIR / "docs"
POSTS_DIR = BASE_DIR / "posts"

SITE_CONFIG = {
    "title":           "教養の教室｜社会人のための知的生活マガジン",
    "url":             "https://kevin62sbiyl-spec.github.io/ehon-blog",
    "author":          "教養の教室",
    "youtube_channel": "https://www.youtube.com/@your-channel",
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
            raw_kw = meta.get("keywords", "")
            meta["keywords"] = [k.strip().strip("[]") for k in raw_kw.split(",") if k.strip()]
            posts.append(meta)
    return posts

def build_search_json(posts):
    """検索用JSONデータを生成"""
    base = SITE_CONFIG["url"]
    data = []
    for p in posts:
        data.append({
            "title":    p.get("title", ""),
            "url":      f"{base}/posts/{p.get('slug','')}.html",
            "category": p.get("category", ""),
            "tags":     p.get("tags", []),
            "keywords": p.get("keywords", []),
            "desc":     p.get("description", ""),
            "date":     p.get("date", ""),
        })
    out = DOCS_DIR / "search.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✅ search.json 生成（{len(data)}記事）")

def build_search_page():
    """検索ページを生成"""
    site_url = SITE_CONFIG["url"]
    yt_ch    = SITE_CONFIG["youtube_channel"]

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>記事を検索 | {SITE_CONFIG['title']}</title>
<meta name="description" content="教養の教室の全記事をキーワード・カテゴリ・タグで検索できます。">
<link rel="canonical" href="{site_url}/search.html">
<link rel="stylesheet" href="assets/css/style.css">
<style>
.search-wrap{{max-width:680px;margin:0 auto;padding:2rem 0 4rem}}
.search-box{{display:flex;gap:10px;margin-bottom:2rem}}
.search-input{{flex:1;font-size:16px;padding:12px 16px;border:1.5px solid var(--border);border-radius:var(--r-lg);background:var(--color-background-primary,#fff);color:var(--ink);transition:border-color .2s}}
.search-input:focus{{outline:none;border-color:var(--accent)}}
.search-btn{{padding:12px 22px;background:var(--ink);color:#fff;border:none;border-radius:var(--r-lg);font-size:14px;font-weight:700;cursor:pointer;transition:opacity .2s}}
.search-btn:hover{{opacity:.82}}
.filter-row{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:1.5rem}}
.filter-btn{{font-size:12px;padding:5px 14px;border:0.5px solid var(--border);border-radius:20px;background:transparent;color:var(--ink-soft);cursor:pointer;transition:all .15s}}
.filter-btn:hover,.filter-btn.active{{background:var(--accent-lt);color:var(--accent);border-color:var(--accent)}}
.result-count{{font-size:13px;color:var(--ink-muted);margin-bottom:1rem}}
.result-item{{background:#fff;border:0.5px solid var(--border);border-radius:var(--r-lg);padding:18px 20px;margin-bottom:12px;transition:box-shadow .2s}}
.result-item:hover{{box-shadow:0 4px 16px rgba(0,0,0,.08)}}
.result-item a{{text-decoration:none;color:inherit}}
.result-cat{{font-size:11px;font-weight:700;color:var(--accent);background:var(--accent-lt);padding:2px 9px;border-radius:20px;display:inline-block;margin-bottom:8px}}
.result-title{{font-size:16px;font-weight:700;color:var(--ink);margin-bottom:6px;line-height:1.45}}
.result-desc{{font-size:13px;color:var(--ink-soft);line-height:1.6;margin-bottom:8px}}
.result-tags{{display:flex;flex-wrap:wrap;gap:5px}}
.result-tag{{font-size:11px;padding:2px 8px;border-radius:20px;background:var(--paper-alt);color:var(--ink-muted);border:0.5px solid var(--border)}}
.result-date{{font-size:11px;color:var(--ink-muted);margin-top:6px}}
.no-result{{text-align:center;padding:3rem;color:var(--ink-muted);font-size:14px}}
.highlight{{background:#fff3cd;border-radius:2px;padding:0 2px}}
</style>
</head>
<body>
<header class="site-header">
  <div class="container">
    <a class="logo" href="index.html">{SITE_CONFIG['author']}</a>
    <nav>
      <a href="index.html">ホーム</a>
      <a href="categories.html">カテゴリ</a>
      <a href="search.html">検索</a>
      <a href="{yt_ch}" target="_blank" rel="noopener">YouTube</a>
    </nav>
  </div>
</header>

<div class="hero" style="padding:40px 0">
  <div class="container">
    <p class="hero-eyebrow">全記事を検索</p>
    <h1 class="hero-title" style="font-size:clamp(22px,4vw,34px)">読みたい記事を探す</h1>
  </div>
</div>

<main class="container">
  <div class="search-wrap">
    <div class="search-box">
      <input class="search-input" id="searchInput" type="text" placeholder="キーワードを入力（例：ソクラテス、資本主義、仏教）" autofocus>
      <button class="search-btn" onclick="doSearch()">検索</button>
    </div>
    <div class="filter-row" id="catFilters"></div>
    <div class="result-count" id="resultCount"></div>
    <div id="results"></div>
  </div>
</main>

<footer class="site-footer">
  <div class="container"><p>© 2025 {SITE_CONFIG['author']}</p></div>
</footer>

<script>
let allPosts = [];
let activeCategory = '';

fetch('search.json')
  .then(r => r.json())
  .then(data => {{
    allPosts = data;
    buildCatFilters();
    const params = new URLSearchParams(location.search);
    const q = params.get('q') || '';
    const cat = params.get('cat') || '';
    if (q) document.getElementById('searchInput').value = q;
    if (cat) activeCategory = cat;
    doSearch();
  }});

function buildCatFilters() {{
  const cats = [...new Set(allPosts.map(p => p.category))].filter(Boolean);
  const wrap = document.getElementById('catFilters');
  wrap.innerHTML = '<button class="filter-btn active" id="cat-all" onclick="setCategory(\\'\\')">すべて</button>' +
    cats.map(c => `<button class="filter-btn" id="cat-${{c}}" onclick="setCategory('${{c}}')">${{c}}</button>`).join('');
}}

function setCategory(cat) {{
  activeCategory = cat;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  const target = cat ? document.getElementById('cat-' + cat) : document.getElementById('cat-all');
  if (target) target.classList.add('active');
  doSearch();
}}

function highlight(text, query) {{
  if (!query) return text;
  const escaped = query.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
  return text.replace(new RegExp(escaped, 'gi'), m => `<mark class="highlight">${{m}}</mark>`);
}}

function doSearch() {{
  const q = document.getElementById('searchInput').value.trim().toLowerCase();
  let results = allPosts;

  if (activeCategory) {{
    results = results.filter(p => p.category === activeCategory);
  }}

  if (q) {{
    results = results.filter(p => {{
      return (p.title + p.desc + p.category + p.tags.join(' ') + p.keywords.join(' ')).toLowerCase().includes(q);
    }});
  }}

  const count = document.getElementById('resultCount');
  const wrap  = document.getElementById('results');

  if (results.length === 0) {{
    count.textContent = '';
    wrap.innerHTML = '<div class="no-result">該当する記事が見つかりませんでした。<br>別のキーワードをお試しください。</div>';
    return;
  }}

  count.textContent = `${{results.length}}件の記事が見つかりました`;
  wrap.innerHTML = results.map(p => {{
    const tags = p.tags.map(t => `<span class="result-tag">${{t}}</span>`).join('');
    return `<div class="result-item">
      <a href="${{p.url}}">
        <span class="result-cat">${{p.category}}</span>
        <p class="result-title">${{highlight(p.title, q)}}</p>
        <p class="result-desc">${{highlight(p.desc, q)}}</p>
        <div class="result-tags">${{tags}}</div>
        <p class="result-date">${{p.date}}</p>
      </a>
    </div>`;
  }}).join('');

  history.replaceState(null,'',`search.html?q=${{encodeURIComponent(q)}}${{activeCategory ? '&cat=' + encodeURIComponent(activeCategory) : ''}}`);
}}

document.getElementById('searchInput').addEventListener('keydown', e => {{
  if (e.key === 'Enter') doSearch();
}});
</script>
</body>
</html>"""

    (DOCS_DIR / "search.html").write_text(html, encoding="utf-8")
    print(f"  ✅ search.html 生成完了")

def add_search_link_to_nav():
    """既存のHTMLファイルのナビに検索リンクを追加"""
    site_url = SITE_CONFIG["url"]
    files = list(DOCS_DIR.glob("*.html")) + list((DOCS_DIR / "posts").glob("*.html"))
    updated = 0
    for f in files:
        html = f.read_text(encoding="utf-8")
        if 'href="search.html"' in html or 'href="../search.html"' in html:
            continue
        # posts/配下かどうかで相対パスを変える
        is_post = "posts" in str(f)
        search_href = "../search.html" if is_post else "search.html"
        # ナビのYouTubeリンクの前に検索リンクを追加
        html = html.replace(
            f'<a href="{site_url}" target="_blank"',
            f'<a href="{search_href}">検索</a><a href="{site_url}" target="_blank"'
        )
        # YouTube外部リンクパターン
        yt_nav = '<a href="https://www.youtube'
        if yt_nav in html:
            html = html.replace(yt_nav, f'<a href="{search_href}">検索</a>{yt_nav}', 1)
        f.write_text(html, encoding="utf-8")
        updated += 1

    print(f"  ✅ ナビに検索リンク追加（{updated}ファイル）")

if __name__ == "__main__":
    print("\n=== サイト内検索機能を追加 ===\n")
    posts = load_all_posts()
    build_search_json(posts)
    build_search_page()
    add_search_link_to_nav()
    print(f"\n完了！反映するには：")
    print(f"git add . && git commit -m 'add: サイト内検索機能' && git push\n")
