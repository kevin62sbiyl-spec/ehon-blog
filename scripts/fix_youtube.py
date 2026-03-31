#!/usr/bin/env python3
"""
YouTube修正スクリプト
- タイトル案セクションを削除
- YouTubeリンクが未設定（@your-channel）の記事はCTAを非表示
- 動画URLを指定して特定記事にリンクを追加する機能付き

使い方:
  全記事を修正:        python scripts/fix_youtube.py
  動画リンクを追加:    python scripts/fix_youtube.py --add "記事スラッグ" "https://youtube.com/watch?v=xxxx"
  例: python scripts/fix_youtube.py --add "momotaro-team-building" "https://youtu.be/xxxx"
"""

import re, sys
from pathlib import Path

BASE_DIR  = Path(__file__).parent.parent
POSTS_OUT = BASE_DIR / "docs" / "posts"

PLACEHOLDER_URL = "https://www.youtube.com/@your-channel"


def fix_html(html: str, youtube_url: str = None) -> str:
    """
    1. youtube-titles セクションを完全削除
    2. youtube_url が未設定ならyoutube-ctaを非表示
    3. youtube_url が設定済みなら正しいURLに差し替え
    """

    # ① タイトル案セクションを削除
    html = re.sub(
        r'<div class="youtube-titles">.*?</div>\s*',
        '',
        html,
        flags=re.DOTALL
    )

    if youtube_url:
        # ② 動画URLを実URLに差し替え（CTAを表示状態に）
        html = html.replace(
            'style="display:none"',
            ''
        )
        # プレースホルダーURLを実URLに置換（youtube-cta内のみ）
        html = re.sub(
            r'(<div class="youtube-cta".*?href=")[^"]*(")',
            rf'\g<1>{youtube_url}\g<2>',
            html,
            flags=re.DOTALL
        )
        # yt-btn のhrefも置換
        html = re.sub(
            r'(<div class="youtube-cta".*?<a href=")[^"]*(")',
            rf'\g<1>{youtube_url}\g<2>',
            html,
            flags=re.DOTALL
        )
    else:
        # ③ プレースホルダーのままならCTAを非表示
        html = re.sub(
            r'<div class="youtube-cta">',
            '<div class="youtube-cta" style="display:none">',
            html
        )

    return html


def fix_all():
    """全記事のHTMLを修正"""
    files = list(POSTS_OUT.glob("*.html"))
    if not files:
        print("❌ docs/posts/ にHTMLファイルが見つかりません")
        return

    fixed = 0
    for f in sorted(files):
        html = f.read_text(encoding="utf-8")

        # すでに実URLが設定されているかチェック
        has_real_url = PLACEHOLDER_URL not in html and 'youtube-cta' in html

        new_html = fix_html(html, youtube_url=None if not has_real_url else "KEEP")
        if new_html != html:
            f.write_text(new_html, encoding="utf-8")
            fixed += 1

    print(f"✅ {fixed}件 修正完了（全{len(files)}記事）")
    print(f"   - YouTubeタイトル案：全記事から削除")
    print(f"   - YouTubeCTA：動画未設定の記事は非表示")
    print(f"\n動画をアップしたら:")
    print(f"  python scripts/fix_youtube.py --add \"記事スラッグ\" \"https://youtu.be/xxxx\"")


def add_youtube_link(slug: str, url: str):
    """特定記事にYouTubeリンクを追加"""
    target = POSTS_OUT / f"{slug}.html"
    if not target.exists():
        # スラッグが部分一致するファイルを探す
        matches = [f for f in POSTS_OUT.glob("*.html") if slug in f.stem]
        if not matches:
            print(f"❌ 記事が見つかりません: {slug}")
            print("利用可能な記事一覧:")
            for f in sorted(POSTS_OUT.glob("*.html")):
                print(f"  {f.stem}")
            return
        target = matches[0]
        print(f"   → {target.stem} を更新します")

    html = target.read_text(encoding="utf-8")

    # CTAを表示状態にしてURLを設定
    # まず非表示を解除
    html = html.replace(
        '<div class="youtube-cta" style="display:none">',
        '<div class="youtube-cta">'
    )
    # プレースホルダーURLを実URLに置換
    html = html.replace(PLACEHOLDER_URL, url)
    # youtube-cta内のhrefを正しいURLに（念のため）
    html = re.sub(
        r'(<div class="youtube-cta".*?<a\s+href=")[^"]*(")',
        rf'\g<1>{url}\g<2>',
        html,
        flags=re.DOTALL
    )

    target.write_text(html, encoding="utf-8")
    print(f"✅ YouTube動画リンクを追加しました")
    print(f"   記事: {target.stem}")
    print(f"   URL:  {url}")
    print(f"\n反映するには:")
    print(f"  git add . && git commit -m \"update: {target.stem} にYouTubeリンク追加\" && git push")


def main():
    args = sys.argv[1:]

    if "--add" in args:
        idx = args.index("--add")
        if idx + 2 >= len(args):
            print("使い方: python scripts/fix_youtube.py --add \"記事スラッグ\" \"https://youtu.be/xxxx\"")
            return
        slug = args[idx + 1]
        url  = args[idx + 2]
        add_youtube_link(slug, url)
    else:
        fix_all()


if __name__ == "__main__":
    main()
