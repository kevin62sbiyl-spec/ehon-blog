#!/usr/bin/env python3
"""
YouTube台本生成スクリプト
使い方: python scripts/make_script.py "https://kevin62sbiyl-spec.github.io/ehon-blog/posts/記事スラッグ.html"
例:    python scripts/make_script.py "https://youtu.be/NgKOSdqOZOI"
       python scripts/make_script.py "taoism-laozi-zhuangzi-wuwei-ziran"
"""

import anthropic, os, sys, re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

BASE_DIR  = Path(__file__).parent.parent
POSTS_DIR = BASE_DIR / "posts"
OUT_DIR   = BASE_DIR / "scripts_output"

SYSTEM = """あなたはYouTube教養動画の台本専門家です。
ブログ記事の内容をもとに、NotebookLMでスライド生成することを前提とした
YouTube解説動画の台本を作成してください。

【構成ルール】
- 全15スライド（S1〜S15）
- 1スライドあたり300〜500文字のナレーション原稿
- そのまま読める自然な話し言葉
- 難しい言葉は使いすぎない（教養系だがわかりやすく）
- 流れ：導入→理解→具体例→まとめ
- 前後のスライドと繋がる構造

【スライド構成の目安】
S1：タイトル・つかみ（視聴者の共感を引く）
S2：導入・今日のテーマ提示
S3：背景・なぜ重要か
S4：基本概念①
S5：基本概念②
S6：具体的なエピソード・事例①
S7：具体的なエピソード・事例②
S8：深掘り①
S9：深掘り②
S10：現代への応用①
S11：現代への応用②
S12：よくある誤解・反論
S13：実践のヒント
S14：関連テーマへの橋渡し
S15：まとめ・CTA

【フォーマット】
【S1｜タイトル】
（スライドに載せるタイトル案）
（ナレーション300〜500文字）

【S2｜導入】
（スライドに載せるタイトル案）
（ナレーション300〜500文字）

...

【S15｜まとめ】
（スライドに載せるタイトル案）
（ナレーション300〜500文字）

【重要】
- 1スライド＝1テーマ
- 内容を詰め込みすぎない
- スライドとナレーションがズレない構造
- 最後のCTAにはチャンネル登録・ブログ誘導を入れる"""


def load_post_content(slug: str) -> tuple[str, str]:
    """Markdownファイルから記事内容を読み込む"""
    matches = list(POSTS_DIR.glob(f"*{slug}*.md"))
    if not matches:
        return "", ""

    f = matches[0]
    lines = f.read_text(encoding="utf-8").split("\n")
    title, body, in_fm = "", [], False
    fm_count = 0

    for line in lines:
        if line.strip() == "---":
            fm_count += 1
            in_fm = fm_count < 2
            continue
        if in_fm:
            if line.startswith("title:"):
                title = line.partition(":")[2].strip().strip('"')
        else:
            body.append(line)

    return title, "\n".join(body)


def generate_script(content: str, title: str) -> str:
    """Claude APIで台本を生成"""
    print(f"  台本生成中: {title[:40]}...")

    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=6000,
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": f"""以下のブログ記事をもとにYouTube台本を作成してください。

タイトル：{title}

記事内容：
{content[:4000]}

15スライド分の台本を作成してください。"""
        }]
    )
    return msg.content[0].text


def save_script(title: str, script: str, slug: str) -> Path:
    """台本をMarkdownファイルとして保存"""
    OUT_DIR.mkdir(exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ts}_{slug[:30]}_script.md"
    path     = OUT_DIR / filename

    content = f"""# YouTube台本
## {title}

生成日時：{datetime.now().strftime("%Y年%m月%d日 %H:%M")}

---

{script}

---

## NotebookLMへの指示文（コピペ用）

以下の文章をもとにYouTube解説動画の台本を作成してください。

【目的】
・スライドと完全一致するナレーション台本を作る
・NotebookLMでスライド生成する前提

【構成】
・全15スライド
・各スライドごとに台本作成

【文字数】
・1スライドあたり200〜400文字

【ルール】
・話す内容として自然な文章にする（そのまま読める）
・難しい言葉は使いすぎない（教養系だが分かりやすく）
・流れを意識する（導入→理解→具体→まとめ）
・前後のスライドと繋がるようにする

【フォーマット】
【S1｜タイトル】
（ナレーション）
【S2｜導入】
（ナレーション）
…
【S15｜まとめ】
（ナレーション）

【重要】
・1スライド＝1テーマ
・内容を詰め込みすぎない
・スライドとナレーションがズレない構造にする

では作成してください。
"""
    path.write_text(content, encoding="utf-8")
    return path


def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(1)

    input_arg = args[0]

    # スラッグ・URLからスラッグを抽出
    if "youtu" in input_arg:
        print("❌ YouTube URLではなく、ブログ記事のURLまたはスラッグを指定してください")
        print("例: python scripts/make_script.py taoism-laozi-zhuangzi-wuwei-ziran")
        sys.exit(1)

    # URLからスラッグを抽出
    slug = input_arg
    if "/" in input_arg:
        slug = input_arg.rstrip("/").split("/")[-1].replace(".html", "")

    print(f"\n{'='*55}")
    print(f"  🎬 YouTube台本生成")
    print(f"  スラッグ: {slug}")
    print(f"{'='*55}\n")

    # 記事内容を読み込む
    title, content = load_post_content(slug)

    if not content:
        print(f"❌ 記事が見つかりません: {slug}")
        print("\n利用可能な記事:")
        for f in sorted(POSTS_DIR.glob("*.md"))[:10]:
            print(f"  {f.stem.split('-', 3)[-1] if '-' in f.stem else f.stem}")
        sys.exit(1)

    print(f"  ✅ 記事読み込み完了: {title}")

    # 台本生成
    script = generate_script(content, title)

    # 保存
    out_path = save_script(title, script, slug)

    print(f"\n{'='*55}")
    print(f"  🎉 台本生成完了！")
    print(f"  📄 保存先: {out_path}")
    print(f"\n  次のステップ:")
    print(f"  1. scripts_output/ フォルダを開く")
    print(f"  2. 台本ファイルをNotebookLMにソースとして追加")
    print(f"  3. 元のブログ記事PDFもソースに追加")
    print(f"  4. ファイル末尾の「NotebookLMへの指示文」をコピペして実行")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
