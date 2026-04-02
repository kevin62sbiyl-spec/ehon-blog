#!/usr/bin/env python3
"""
社会人教養ブログ 自動生成システム
--------------------------------------------------
使い方:
  記事1本:  python scripts/generate.py "ソクラテスとは何者か"
  100本一括: python scripts/generate.py --bulk
  カテゴリ指定: python scripts/generate.py --bulk --category お金と資本
"""

import anthropic, json, os, re, sys, time
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# ── 設定 ──────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).parent.parent
POSTS_DIR = BASE_DIR / "posts"
DOCS_DIR  = BASE_DIR / "docs"
POSTS_OUT = DOCS_DIR / "posts"

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

SITE_CONFIG = {
    "title":       "教養の教室｜社会人のための知的生活マガジン",
    "description": "お金・宗教・哲学・歴史・芸術・言語。6つの教養で人生の解像度を上げるブログ。",
    "url":         "https://kevin62sbiyl-spec.github.io/ehon-blog",
    "author":      "教養の教室",
    "youtube_channel": "https://www.youtube.com/@your-channel",
}

# ── 6テーマ × 各17本 = 102本のテーマリスト ───────────────────
BULK_THEMES = {
    "お金と資本": [
        "資本主義とは何か｜お金が世界を動かす仕組み",
        "複利の魔法｜アインシュタインが「世界第8の不思議」と呼んだ理由",
        "インフレとデフレ｜物価が動くとき何が起きているのか",
        "株式会社の誕生｜東インド会社が変えた世界のルール",
        "貨幣の歴史｜なぜ紙切れに価値が生まれたのか",
        "ケインズ経済学入門｜政府はなぜお金を使うべきなのか",
        "マルクスの資本論｜現代人が読むべき理由",
        "中央銀行の役割｜日本銀行は何をしているのか",
        "格差社会の構造｜ピケティが示した富の偏在",
        "税金の哲学｜なぜ人は税を払うのか",
        "保険の本質｜リスクを社会で分かち合う仕組み",
        "不動産投資の論理｜土地に価値が生まれる理由",
        "仮想通貨と国家｜ビットコインが問いかけるもの",
        "行動経済学入門｜人はなぜ不合理な選択をするのか",
        "グローバリゼーションの功罪｜世界はつながって豊かになったか",
        "シリコンバレー型資本主義｜なぜスタートアップが世界を変えるのか",
        "SDGsと資本主義｜利益と持続可能性は両立するか",
    ],
    "宗教": [
        "宗教とは何か｜なぜ人は神を必要とするのか",
        "キリスト教入門｜20億人が信じる世界最大の宗教",
        "イスラム教入門｜誤解されがちな14億人の信仰",
        "仏教入門｜釈迦が悟った「苦しみからの解放」",
        "神道とは何か｜日本人が知らない自国の宗教",
        "ユダヤ教入門｜世界を動かす「選ばれた民」の思想",
        "ヒンドゥー教入門｜多神教の豊かな宇宙観",
        "宗教改革｜ルターがカトリックに挑んだ理由",
        "宗教と科学｜なぜ対立し、どこで融和するのか",
        "宗教と戦争｜神の名のもとに起きた歴史的衝突",
        "新興宗教の心理学｜なぜ人はカルトに引き込まれるか",
        "死後の世界観比較｜各宗教は「死」をどう捉えるか",
        "瞑想の科学｜仏教的実践が脳に与える効果",
        "宗教と資本主義｜プロテスタンティズムが経済を変えた",
        "無宗教社会の行方｜神なき時代をどう生きるか",
        "宗教と倫理｜善悪の基準はどこから来るのか",
        "日本人の宗教観｜なぜ初詣もクリスマスもやるのか",
    ],
    "哲学・思想": [
        "哲学とは何か｜2500年の問いが今も続く理由",
        "ソクラテスの問答法｜「無知の知」が変えた思考法",
        "プラトンのイデア論｜影の洞窟から真実を見る",
        "アリストテレスの論理学｜西洋思想の父が作った知の体系",
        "デカルトの「我思う、ゆえに我あり」｜疑うことから始まる哲学",
        "カントの純粋理性批判｜人はどこまで世界を知れるか",
        "ニーチェの超人思想｜神は死んだ後に何が来るか",
        "実存主義入門｜サルトルが言った「実存は本質に先立つ」",
        "功利主義入門｜最大多数の最大幸福は正しいか",
        "マルクス主義哲学｜物質が歴史を動かすという思想",
        "東洋哲学入門｜老子・荘子の「無為自然」を読む",
        "現象学入門｜フッサールが問いかけた意識の構造",
        "構造主義入門｜レヴィ＝ストロースが解いた文化の謎",
        "分析哲学入門｜言語が思考を規定するという発見",
        "幸福論の系譜｜哲学者たちはどう「幸せ」を定義したか",
        "自由意志は存在するか｜哲学と脳科学の交差点",
        "AI時代の哲学｜機械が考えるとき人間とは何か",
    ],
    "歴史": [
        "文明の誕生｜なぜメソポタミアから歴史が始まったのか",
        "古代ローマ帝国の興亡｜なぜ1000年続いた帝国は滅びたか",
        "モンゴル帝国とは何か｜史上最大の陸上帝国の秘密",
        "ルネサンスとは何か｜なぜイタリアで人間が蘇ったのか",
        "大航海時代｜ヨーロッパが世界を「発見」した意味",
        "産業革命｜蒸気機関が人類の生活を変えた瞬間",
        "フランス革命｜自由・平等・博愛が生まれた代償",
        "第一次世界大戦の原因｜なぜ一発の銃弾が世界を変えたか",
        "大恐慌1929｜株価暴落が世界をどう変えたか",
        "第二次世界大戦の教訓｜人類史最大の悲劇から何を学ぶか",
        "冷戦とは何か｜核の恐怖が支配した半世紀",
        "植民地主義の遺産｜なぜ途上国は貧しいままなのか",
        "日本史を世界史で読む｜鎖国・開国・近代化の真の意味",
        "シルクロードの歴史｜東西文明をつないだ交易路",
        "ペストと歴史｜感染症が社会構造を変えてきた",
        "革命の構造｜なぜ体制は突然崩壊するのか",
        "歴史の見方｜過去をどう読めば未来が見えるか",
    ],
    "芸術": [
        "芸術とは何か｜美しさの基準はどこにあるのか",
        "印象派革命｜モネたちがなぜ美術界を変えられたか",
        "ピカソと立体主義｜絵画が「見る」を問い直した瞬間",
        "音楽の構造｜なぜ人は音に感動するのか",
        "バッハからビートルズへ｜西洋音楽500年の流れ",
        "映画の誕生と進化｜20世紀最大の芸術が生まれた経緯",
        "建築は思想である｜ガウディ・コルビュジエが問いかけたこと",
        "日本美術の特質｜侘び寂び・余白・非対称の美学",
        "現代アートはなぜわからないのか｜デュシャンの便器から考える",
        "デザインと芸術の違い｜機能と美はどう共存するか",
        "ルーブル美術館で考える｜傑作が語る人類の歴史",
        "音楽と感情の科学｜なぜ曲を聴いて泣けるのか",
        "写真の哲学｜カメラが切り取る「現実」とは何か",
        "漫画・アニメは芸術か｜日本が生んだ表現の可能性",
        "アートマーケットの構造｜なぜ絵に数十億円の値がつくのか",
        "創造性とは何か｜天才と凡人の違いはどこにあるか",
        "AIと芸術｜機械が作る美は本物の芸術か",
    ],
    "言葉と文学": [
        "言語とは何か｜人間だけが言葉を持つ理由",
        "文字の誕生｜楔形文字から始まった知の革命",
        "ホメロスの叙事詩｜イリアスとオデュッセイアが語るもの",
        "シェイクスピアとは何者か｜400年読まれ続ける理由",
        "夏目漱石と近代日本語｜言文一致運動が変えた思考",
        "カフカの不条理文学｜なぜ変身は名作なのか",
        "村上春樹の世界文学性｜なぜ世界中で読まれるのか",
        "詩の読み方｜言葉を圧縮する芸術の楽しみ方",
        "翻訳の哲学｜言語の壁を越えることの限界と可能性",
        "比喩の力｜メタファーが思考を形作るしくみ",
        "日本語の特質｜世界で最も複雑な言語の構造",
        "言語と思考の関係｜言葉は世界の見え方を変えるか",
        "神話の構造｜世界中の物語に共通するパターン",
        "読書の技法｜知識を血肉にする本の読み方",
        "ソーシャルメディアと言語変化｜SNSは文化を壊すか",
        "プロパガンダの言語学｜言葉でいかに人を操るか",
        "AIと言語｜ChatGPTは「理解」しているのか",
    ],
}

# ── AIコンテンツ生成 ─────────────────────────────────────────
def generate_content(theme: str, category: str) -> dict:
    # スタイル判定（テーマによって初心者向けか深掘りかを変える）
    deep_keywords = ["構造", "哲学", "論理", "批判", "主義", "理論", "本質", "科学"]
    style = "深掘り型（中級者向け・専門用語を適切に使い概念を丁寧に解説）" \
        if any(k in theme for k in deep_keywords) \
        else "噛み砕き型（初心者向け・わかりやすい言葉と具体例で解説）"

    system = f"""あなたは「社会人教養ブログ」の専門家AIチームです。
カテゴリ「{category}」の記事を{style}で生成します。

【AI組織の役割分担】
- 編集長：記事の方針・構成を決定
- ライター：本文を執筆（面白さで勝負）
- ファクトチェッカー：年号・人名・書籍情報・歴史的事実を厳密に確認
- SEO担当：キーワード・タイトル・メタ情報を最適化

【ファクトチェック必須ルール】
- 年号・人名・地名は必ず正確に記載
- 書籍名・著者名は原典に忠実に
- 「〜と言われている」など曖昧な表現は使わず根拠を明示
- 不確かな情報は記載しない

【面白さの必須ルール】
- 各セクションに必ず「へえ！」となる具体的エピソードを1つ入れる
- 冒頭は読者の「あるある」な疑問・悩みから始める
- 抽象論だけで終わらず必ず現代生活への示唆で締める
- 数字・固有名詞・具体例を積極的に使う

【視覚強調ルール】
- point_box：各セクションの核心を1〜3行でまとめたボックス
- highlight：特に重要な一文（各セクション1つ）
- profile：人物紹介がある場合はプロフィール情報
- key_facts：数字・年号など覚えておくべき重要データ（3〜5個）

以下のJSON形式のみで返してください（前置き・コードブロック不要）。

{{
  "slug": "英小文字ハイフン区切り・30文字以内",
  "title": "SEOタイトル（28〜35文字）",
  "description": "メタディスクリプション（115〜125文字）",
  "keywords": ["KW1","KW2","KW3","KW4","KW5"],
  "category": "{category}",
  "tags": ["タグ1","タグ2","タグ3"],
  "reading_time": 10,
  "style": "{style}",
  "profile": {{
    "name": "記事の主人公となる人物名（なければ空文字）",
    "birth_death": "生没年（例：1724〜1804）",
    "nationality": "国籍・出身",
    "known_for": "代表的な業績・著作（50文字）"
  }},
  "key_facts": [
    {{"label": "データラベル", "value": "具体的な数字・年号・事実"}}
  ],
  "intro": "読者の疑問・興味から始まる導入文（280文字）",
  "sections": [
    {{
      "h2": "セクション見出し",
      "body": "本文（500文字以上。具体的エピソード・歴史的事実・現代への示唆を含む）",
      "highlight": "このセクションで最も重要な一文（60文字以内）",
      "point_box": "核心をまとめたポイント（80文字以内）",
      "h3s": [
        {{"h3": "小見出し", "body": "本文（200文字）"}}
      ]
    }}
  ],
  "conclusion": "読者が行動・思考したくなるまとめ（200文字）",
  "youtube": {{
    "hook": "YouTube冒頭30秒のフック台本",
    "title_ideas": ["タイトル案1","タイトル案2","タイトル案3"],
    "cta_text": "動画への誘導テキスト（60文字）"
  }},
  "book_recommendations": [
    {{"title": "書名", "author": "著者名", "reason": "おすすめ理由（50文字）", "amazon_keyword": "Amazon検索KW"}}
  ],
  "related_themes": ["関連テーマ1","関連テーマ2","関連テーマ3"]
}}

sectionsは5つ作成。各bodyは必ず500文字以上。book_recommendationsは2〜3冊。key_factsは3〜5個。"""

    for attempt in range(3):
        try:
            msg = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=8000,
                system=system,
                messages=[{"role": "user", "content": f"テーマ：「{theme}」\nカテゴリ：{category}\n\n記事を生成してください。"}]
            )
            text  = msg.content[0].text
            clean = re.sub(r"```json|```", "", text).strip()
            return json.loads(clean)
        except Exception as e:
            if attempt < 2:
                print(f"    ⚠️  リトライ中 ({attempt+1}/3)...")
                time.sleep(5)
            else:
                raise e


# ── Markdown保存 ─────────────────────────────────────────────
def save_markdown(data: dict, date_str: str) -> Path:
    slug     = data.get("slug", "article")
    filename = f"{date_str}-{slug}.md"
    path     = POSTS_DIR / filename
    POSTS_DIR.mkdir(exist_ok=True)

    sections_md = ""
    for sec in data.get("sections", []):
        sections_md += f"\n## {sec['h2']}\n\n{sec['body']}\n"
        for h3 in sec.get("h3s", []):
            sections_md += f"\n### {h3['h3']}\n\n{h3['body']}\n"

    books_md = "\n".join([
        f"- **『{b['title']}』{b['author']}**：{b['reason']}（Amazon検索：`{b['amazon_keyword']}`）"
        for b in data.get("book_recommendations", [])
    ])

    tags_str = ", ".join(data.get("tags", []))
    kw_str   = ", ".join(data.get("keywords", []))

    content = f"""---
title: "{data['title']}"
description: "{data['description']}"
date: "{date_str}"
slug: "{slug}"
category: "{data.get('category','教養')}"
tags: [{tags_str}]
keywords: [{kw_str}]
reading_time: {data.get('reading_time', 10)}
style: "{data.get('style','')}"
---

{data['intro']}

{sections_md}

## まとめ

{data['conclusion']}

---

## 📺 YouTube動画でも解説

{data.get('youtube',{}).get('cta_text','')}

## 📚 おすすめ書籍

{books_md}
"""
    path.write_text(content, encoding="utf-8")
    return path


# ── HTML記事生成 ──────────────────────────────────────────────
def generate_article_html(data: dict, date_str: str, all_posts: list) -> tuple:
    slug      = data["slug"]
    title     = data["title"]
    desc      = data["description"]
    category  = data.get("category", "教養")
    site_url  = SITE_CONFIG["url"]
    yt_ch     = SITE_CONFIG["youtube_channel"]
    yt        = data.get("youtube", {})

    tags_html = "".join([f'<span class="tag">{t}</span>' for t in data.get("tags", [])])
    toc_items = "".join([
        f'<li><a href="#s{i}">{sec["h2"]}</a></li>'
        for i, sec in enumerate(data.get("sections", []))
    ])

    # プロフィールカード
    profile = data.get("profile", {})
    profile_html = ""
    if profile.get("name"):
        profile_html = f'<div class="profile-card"><div class="profile-icon">{profile["name"][0]}</div><div class="profile-info"><p class="profile-name">{profile["name"]}</p><p class="profile-meta">{profile.get("birth_death","")} ／ {profile.get("nationality","")}</p><p class="profile-known">{profile.get("known_for","")}</p></div></div>'

    # キーファクト
    key_facts = data.get("key_facts", [])
    keyfact_html = ""
    if key_facts:
        items = "".join([f'<div class="kf-item"><span class="kf-label">{f["label"]}</span><span class="kf-value">{f["value"]}</span></div>' for f in key_facts])
        keyfact_html = f'<div class="key-facts">{items}</div>'

    body_html = f'<p class="intro">{data["intro"]}</p>'
    if profile_html:
        body_html += profile_html
    if keyfact_html:
        body_html += keyfact_html

    for i, sec in enumerate(data.get("sections", [])):
        body_html += f'<h2 id="s{i}">{sec["h2"]}</h2>'
        if sec.get("highlight"):
            body_html += f'<p class="highlight-text">{sec["highlight"]}</p>'
        body_html += f'<p>{sec["body"]}</p>'
        if sec.get("point_box"):
            body_html += f'<div class="point-box"><span class="point-label">POINT</span><p>{sec["point_box"]}</p></div>'
        for h3 in sec.get("h3s", []):
            body_html += f'<h3>{h3["h3"]}</h3><p>{h3["body"]}</p>'

    books_html = "".join([
        f'<div class="book-item"><div class="book-info"><strong>『{b["title"]}』</strong><span class="book-author">{b["author"]}</span><p>{b["reason"]}</p></div>'
        f'<a href="https://www.amazon.co.jp/s?k={b["amazon_keyword"].replace(" ","+")}" target="_blank" rel="noopener nofollow" class="amazon-btn">Amazonで見る →</a></div>'
        for b in data.get("book_recommendations", [])
    ])

    yt_titles_html = "".join([f"<li>{t}</li>" for t in yt.get("title_ideas", [])])

    others = [p for p in all_posts if p.get("slug") != slug][:4]
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
<title>{title} | {SITE_CONFIG['title']}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{', '.join(data.get('keywords',[]))}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{site_url}/posts/{slug}.html">
<link rel="canonical" href="{site_url}/posts/{slug}.html">
<link rel="stylesheet" href="../assets/css/style.css">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"BlogPosting","headline":"{title}","description":"{desc}","datePublished":"{date_str}","author":{{"@type":"Person","name":"{SITE_CONFIG['author']}"}}}}
</script>
</head>
<body>
<header class="site-header">
  <div class="container">
    <a class="logo" href="../index.html">{SITE_CONFIG['author']}</a>
    <nav>
      <a href="../index.html">ホーム</a>
      <a href="../categories.html">カテゴリ</a>
      <a href="{yt_ch}" target="_blank" rel="noopener">YouTube</a>
    </nav>
  </div>
</header>
<main class="article-layout container">
  <article class="article-body">
    <div class="article-meta">
      <a class="category-badge" href="../categories.html#{category}">{category}</a>
      <time datetime="{date_str}">{date_str}</time>
      <span class="reading-time">約{data.get('reading_time',10)}分</span>
    </div>
    <h1 class="article-title">{title}</h1>
    <div class="tags">{tags_html}</div>
    <nav class="toc"><p class="toc-title">目次</p><ol>{toc_items}</ol></nav>
    <div class="article-content">{body_html}</div>
    <div class="conclusion-box"><h2>まとめ</h2><p>{data['conclusion']}</p></div>
    <div class="youtube-cta">
      <div class="yt-icon">▶</div>
      <div>
        <p class="yt-label">YouTube動画でも解説しています</p>
        <p class="yt-hook">{yt.get('hook','')}</p>
        <a href="{yt_ch}" target="_blank" rel="noopener" class="yt-btn">チャンネルを見る →</a>
      </div>
    </div>
    <div class="book-section"><p class="section-label">📚 おすすめ書籍</p>{books_html}</div>
    <div class="related-section"><p class="section-label">関連記事</p><div class="related-cards">{related_html}</div></div>
  </article>
  <aside class="sidebar">
    <div class="sidebar-widget">
      <p class="widget-title">カテゴリ</p>
      <div class="cat-links">
        {"".join(f'<a href="../categories.html#{c}" class="cat-link">{c}</a>' for c in BULK_THEMES.keys())}
      </div>
    </div>
    <div class="sidebar-widget">
      <p class="widget-title">📺 YouTubeチャンネル</p>
      <p style="font-size:13px;line-height:1.6;margin-bottom:12px">教養を動画でわかりやすく解説中</p>
      <a href="{yt_ch}" target="_blank" rel="noopener" class="yt-btn" style="display:block;text-align:center">チャンネル登録 →</a>
    </div>
  </aside>
</main>
<footer class="site-footer">
  <div class="container"><p>© 2025 {SITE_CONFIG['author']} | <a href="{yt_ch}" target="_blank" rel="noopener">YouTube</a></p></div>
</footer>
<script src="../assets/js/main.js"></script>
</body>
</html>"""
    return slug, html


# ── トップページ生成 ──────────────────────────────────────────
def generate_index_html(all_posts: list) -> str:
    site_url  = SITE_CONFIG["url"]
    yt_ch     = SITE_CONFIG["youtube_channel"]

    # カテゴリ別に最新1件をフィーチャー
    featured = {}
    for p in all_posts:
        cat = p.get("category", "")
        if cat not in featured:
            featured[cat] = p

    feat_html = "".join([
        f'<a class="feat-card" href="{site_url}/posts/{p["slug"]}.html">'
        f'<span class="category-badge">{cat}</span>'
        f'<h3>{p["title"]}</h3>'
        f'<p>{p["description"]}</p></a>'
        for cat, p in featured.items()
    ])

    cards = "".join([
        f'<a class="post-card" href="{site_url}/posts/{p["slug"]}.html">'
        f'<div class="card-meta"><span class="category-badge">{p.get("category","教養")}</span><time>{p.get("date","")}</time></div>'
        f'<h2 class="card-title">{p["title"]}</h2>'
        f'<p class="card-desc">{p["description"]}</p>'
        f'<div class="card-tags">{"".join(f"<span class=\'tag\'>{t}</span>" for t in p.get("tags",[])[:3])}</div>'
        f'<span class="card-reading">約{p.get("reading_time",10)}分</span></a>'
        for p in all_posts
    ])

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{SITE_CONFIG['title']}</title>
<meta name="description" content="{SITE_CONFIG['description']}">
<meta property="og:title" content="{SITE_CONFIG['title']}">
<meta property="og:description" content="{SITE_CONFIG['description']}">
<link rel="canonical" href="{site_url}/">
<link rel="stylesheet" href="assets/css/style.css">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Blog","name":"{SITE_CONFIG['title']}","description":"{SITE_CONFIG['description']}","url":"{site_url}"}}
</script>
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
<div class="hero">
  <div class="container">
    <p class="hero-eyebrow">お金 / 宗教 / 哲学 / 歴史 / 芸術 / 言葉</p>
    <h1 class="hero-title">知ることで、<br>人生の解像度が上がる。</h1>
    <p class="hero-sub">{SITE_CONFIG['description']}</p>
    <a href="{yt_ch}" target="_blank" rel="noopener" class="hero-yt-btn">▶ YouTubeでも発信中</a>
  </div>
</div>
<main class="container">
  <p class="section-heading">カテゴリ別おすすめ</p>
  <div class="feat-grid">{feat_html}</div>
  <p class="section-heading">全記事一覧</p>
  <div class="posts-grid">{cards}</div>
</main>
<footer class="site-footer">
  <div class="container"><p>© 2025 {SITE_CONFIG['author']}</p></div>
</footer>
<script src="assets/js/main.js"></script>
</body>
</html>"""


# ── 記事データ読み込み ────────────────────────────────────────
def load_all_posts() -> list:
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


# ── サイトビルド ──────────────────────────────────────────────
def build_site():
    POSTS_OUT.mkdir(parents=True, exist_ok=True)
    all_posts = load_all_posts()

    for f in sorted(POSTS_DIR.glob("*.md"), reverse=True):
        meta, in_fm = {}, False
        for line in f.read_text(encoding="utf-8").split("\n"):
            if line.strip() == "---":
                in_fm = not in_fm; continue
            if in_fm and ":" in line:
                k, _, v = line.partition(":")
                meta[k.strip()] = v.strip().strip('"')
        if not meta.get("slug"):
            continue
        data = {
            "slug": meta.get("slug", ""),
            "title": meta.get("title", ""),
            "description": meta.get("description", ""),
            "category": meta.get("category", "教養"),
            "tags": [t.strip().strip("[]") for t in meta.get("tags", "").split(",") if t.strip()],
            "keywords": [],
            "reading_time": int(meta.get("reading_time", 10)),
            "intro": "", "sections": [], "conclusion": "",
            "youtube": {"hook": "", "title_ideas": [], "cta_text": ""},
            "book_recommendations": [],
        }
        slug, html = generate_article_html(data, meta.get("date", ""), all_posts)
        (POSTS_OUT / f"{slug}.html").write_text(html, encoding="utf-8")

    (DOCS_DIR / "index.html").write_text(generate_index_html(all_posts), encoding="utf-8")
    print(f"  ✅ サイトビルド完了（{len(all_posts)}記事）")


# ── 一括生成 ─────────────────────────────────────────────────
def bulk_generate(target_category: str = None):
    themes_to_gen = {}
    if target_category:
        if target_category in BULK_THEMES:
            themes_to_gen[target_category] = BULK_THEMES[target_category]
        else:
            print(f"カテゴリ '{target_category}' が見つかりません")
            print("利用可能:", list(BULK_THEMES.keys()))
            return
    else:
        themes_to_gen = BULK_THEMES

    total   = sum(len(v) for v in themes_to_gen.values())
    current = 0
    errors  = []

    # 日付を1日ずつずらして投稿日を分散
    base_date = datetime.now()

    print(f"\n{'='*55}")
    print(f"  📚 一括生成開始：{total}記事")
    print(f"{'='*55}\n")

    for category, themes in themes_to_gen.items():
        print(f"\n【{category}】{len(themes)}記事")
        for i, theme in enumerate(themes):
            current += 1
            date_str = (base_date - timedelta(days=current)).strftime("%Y-%m-%d")
            print(f"  [{current}/{total}] {theme[:30]}...")
            try:
                data = generate_content(theme, category)
                save_markdown(data, date_str)

                # 記事HTMLをその場でビルド
                all_posts = load_all_posts()
                POSTS_OUT.mkdir(parents=True, exist_ok=True)
                slug, html = generate_article_html(data, date_str, all_posts)
                (POSTS_OUT / f"{slug}.html").write_text(html, encoding="utf-8")
                print(f"    ✅ 完了: {data['title'][:35]}")

                # レート制限対策（3秒待機）
                time.sleep(3)
            except Exception as e:
                print(f"    ❌ エラー: {e}")
                errors.append({"theme": theme, "category": category, "error": str(e)})

    # 最後にトップページ再ビルド
    all_posts = load_all_posts()
    (DOCS_DIR / "index.html").write_text(generate_index_html(all_posts), encoding="utf-8")

    print(f"\n{'='*55}")
    print(f"  🎉 一括生成完了！")
    print(f"  成功: {total - len(errors)}記事")
    if errors:
        print(f"  失敗: {len(errors)}記事")
        for e in errors:
            print(f"    - [{e['category']}] {e['theme']}")
    print(f"\n  次のステップ:")
    print(f"  git add . && git commit -m 'add: 100記事一括追加' && git push")
    print(f"{'='*55}\n")


# ── メイン ───────────────────────────────────────────────────
def main():
    args = sys.argv[1:]

    if "--bulk" in args:
        cat = None
        if "--category" in args:
            idx = args.index("--category")
            if idx + 1 < len(args):
                cat = args[idx + 1]
        bulk_generate(cat)
        return

    if not args:
        print(__doc__)
        sys.exit(1)

    theme    = args[0]
    category = args[1] if len(args) > 1 else "教養"

    print(f"\n{'='*55}")
    print(f"  📚 記事生成: {theme}")
    print(f"{'='*55}")

    date_str = datetime.now().strftime("%Y-%m-%d")
    data = generate_content(theme, category)
    save_markdown(data, date_str)

    POSTS_OUT.mkdir(parents=True, exist_ok=True)
    all_posts = load_all_posts()
    slug, html = generate_article_html(data, date_str, all_posts)
    (POSTS_OUT / f"{slug}.html").write_text(html, encoding="utf-8")
    (DOCS_DIR / "index.html").write_text(generate_index_html(all_posts), encoding="utf-8")

    print(f"\n  ✅ 完了: {data['title']}")
    print(f"  🔗 /posts/{slug}.html")
    print(f"\n  git add . && git commit -m 'add: {theme[:20]}' && git push")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
