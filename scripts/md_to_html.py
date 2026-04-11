#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md_to_html.py
使い方: python scripts/md_to_html.py posts/your-article.md カテゴリ名
例:    python scripts/md_to_html.py posts/minimalist-thinking-modern-society.md 哲学・思想
"""

import sys
import os
import re
from datetime import date

# ----------------------------------------
# カテゴリ→URLマッピング
# ----------------------------------------
CATEGORY_MAP = {
    "哲学・思想":   "哲学・思想",
    "お金と資本":   "お金と資本",
    "お金・資本":   "お金と資本",
    "宗教":         "宗教",
    "歴史":         "歴史",
    "芸術":         "芸術",
    "言葉と文学":   "言葉と文学",
    "言語・文学":   "言葉と文学",
    "IT":           "IT",
    "教養の基礎":   "教養の基礎",
}

NAV_HTML = """\
<nav>
  <a href="https://kyoyo-kyoshitsu.com/index.html">教養の教室</a>
  <a href="https://kyoyo-kyoshitsu.com/index.html">ホーム</a>
  <a href="https://kyoyo-kyoshitsu.com/categories.html">カテゴリ</a>
  <a href="https://kyoyo-kyoshitsu.com/search.html">検索</a>
  <a href="https://youtube.com/channel/UCHY3Z0Z4qRdANa_TMKb8v3A">YouTube</a>
</nav>"""

FOOTER_HTML = """\
<footer>
  <p>© 2025 教養の教室 | <a href="https://youtube.com/channel/UCHY3Z0Z4qRdANa_TMKb8v3A">YouTube</a></p>
</footer>"""


def md_to_html_body(md_text):
    """Markdownの本文をHTMLに変換する（シンプル版）"""
    lines = md_text.split("\n")
    html_lines = []
    in_paragraph = False

    for line in lines:
        stripped = line.strip()

        # H1
        if stripped.startswith("# ") and not stripped.startswith("## "):
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            text = stripped[2:]
            html_lines.append(f'<h1>{text}</h1>')

        # H2
        elif stripped.startswith("## ") and not stripped.startswith("### "):
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            text = stripped[3:]
            html_lines.append(f'<h2>{text}</h2>')

        # H3
        elif stripped.startswith("### "):
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False
            text = stripped[4:]
            html_lines.append(f'<h3>{text}</h3>')

        # 空行
        elif stripped == "":
            if in_paragraph:
                html_lines.append("</p>")
                in_paragraph = False

        # 通常テキスト
        else:
            # インライン処理: **bold**
            text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
            if not in_paragraph:
                html_lines.append("<p>")
                in_paragraph = True
            html_lines.append(text)

    if in_paragraph:
        html_lines.append("</p>")

    return "\n".join(html_lines)


def estimate_read_time(text):
    """日本語文字数から読了時間を推定（400字/分）"""
    char_count = len(re.sub(r'\s', '', text))
    minutes = max(1, round(char_count / 400))
    return f"約{minutes}分"


def extract_title(md_text):
    """# タイトル を抽出"""
    for line in md_text.split("\n"):
        if line.startswith("# ") and not line.startswith("## "):
            return line[2:].strip()
    return "記事タイトル"


def build_html(md_text, category_raw, slug):
    category = CATEGORY_MAP.get(category_raw, category_raw)
    title = extract_title(md_text)
    today = date.today().strftime("%Y-%m-%d")
    read_time = estimate_read_time(md_text)
    body_html = md_to_html_body(md_text)
    cat_url = f"https://kyoyo-kyoshitsu.com/categories.html#{category}"

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | 教養の教室｜社会人のための知的生活マガジン</title>
  <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
{NAV_HTML}

<article>
  <div class="article-meta">
    <a href="{cat_url}">{category}</a>
    <time>{today}</time>
    <span>{read_time}</span>
  </div>

  <div class="article-body">
{body_html}
  </div>

</article>

{FOOTER_HTML}
</body>
</html>"""
    return html


def main():
    if len(sys.argv) < 3:
        print("使い方: python scripts/md_to_html.py posts/article.md カテゴリ名")
        sys.exit(1)

    md_path = sys.argv[1]
    category = sys.argv[2]

    if not os.path.exists(md_path):
        print(f"エラー: {md_path} が見つかりません")
        sys.exit(1)

    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # slug = ファイル名（拡張子なし）
    slug = os.path.splitext(os.path.basename(md_path))[0]

    html = build_html(md_text, category, slug)

    # 出力先: docs/posts/slug.html
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(md_path)))
    out_dir = os.path.join(base_dir, "docs", "posts")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{slug}.html")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ HTML生成完了: {out_path}")
    print(f"   URL: https://kyoyo-kyoshitsu.com/posts/{slug}.html")


if __name__ == "__main__":
    main()
