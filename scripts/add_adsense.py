#!/usr/bin/env python3
"""
AdSenseコードを全HTMLファイルの<head>に追加するスクリプト
使い方: python scripts/add_adsense.py
"""

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "docs"

ADSENSE_CODE = '''<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4052981243530641"
     crossorigin="anonymous"></script>'''

def add_adsense():
    # docs直下のHTMLと docs/posts/のHTML全て対象
    html_files = list(DOCS_DIR.glob("*.html")) + list((DOCS_DIR / "posts").glob("*.html"))

    updated = 0
    skipped = 0

    for f in sorted(html_files):
        html = f.read_text(encoding="utf-8")

        # すでに追加済みならスキップ
        if "ca-pub-4052981243530641" in html:
            skipped += 1
            continue

        # <head>の直後に追加
        new_html = html.replace(
            "<head>",
            f"<head>\n{ADSENSE_CODE}"
        )

        f.write_text(new_html, encoding="utf-8")
        updated += 1

    print(f"✅ AdSenseコード追加完了")
    print(f"   更新: {updated}ファイル")
    print(f"   スキップ（追加済み）: {skipped}ファイル")
    print(f"\n反映するには:")
    print(f"  git add . && git commit -m 'add: AdSenseコード追加' && git push")

if __name__ == "__main__":
    add_adsense()
