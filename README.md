# 📚 絵本の教室 — 自動ブログシステム

**「教養×絵本×子育て×社会人」完全自動ブログ**

テーマを1つ入力するだけで、SEO記事 + YouTube台本 + サイト更新が自動で完了します。

---

## ⚡ クイックスタート（3ステップ）

```bash
# 1. セットアップ
pip install -r requirements.txt
cp .env.example .env
# .env を開いて ANTHROPIC_API_KEY を入れる

# 2. 記事を生成してサイト更新
python scripts/generate.py "ももたろうから学ぶチームの作り方"

# 3. GitHubに push → 自動公開
git add . && git commit -m "add: 新記事" && git push
```

---

## 📁 フォルダ構成

```
ehon-blog/
├── scripts/
│   └── generate.py          ← ★ メインスクリプト（これだけ実行する）
├── posts/                   ← Markdown記事の保存場所
│   └── 2025-03-30-xxx.md
├── docs/                    ← GitHub Pagesの公開フォルダ
│   ├── index.html           ← トップページ（自動生成）
│   ├── posts/               ← 記事HTML（自動生成）
│   └── assets/
│       ├── css/style.css    ← デザイン
│       └── js/main.js       ← インタラクション
├── .github/
│   └── workflows/deploy.yml ← GitHub Actions（push時に自動デプロイ）
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 GitHub Pagesで公開する手順

### 1. GitHubリポジトリを作成

1. https://github.com/new を開く
2. リポジトリ名：`ehon-blog`（または任意の名前）
3. Public を選択
4. 「Create repository」をクリック

### 2. ローカルと接続

```bash
cd ehon-blog
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/あなたのID/ehon-blog.git
git push -u origin main
```

### 3. GitHub Pagesを有効化

1. リポジトリの「Settings」を開く
2. 左メニュー「Pages」をクリック
3. Source → 「GitHub Actions」を選択
4. 保存

### 4. 確認

数分後に `https://あなたのID.github.io/ehon-blog/` でサイトが公開されます。

---

## ✏️ 記事を追加する（1コマンド）

```bash
python scripts/generate.py "アリとキリギリスから学ぶ資産形成"
git add . && git commit -m "add: アリとキリギリス記事" && git push
```

以上です。これだけでブログに記事が追加され、自動でサイトが更新されます。

---

## ⚙️ カスタマイズ

`scripts/generate.py` の上部にある `SITE_CONFIG` を編集してください：

```python
SITE_CONFIG = {
    "title":           "あなたのブログタイトル",
    "description":     "ブログの説明文",
    "url":             "https://あなたのID.github.io/ehon-blog",
    "author":          "あなたの名前",
    "youtube_channel": "https://www.youtube.com/@あなたのチャンネル",
}
```

---

## 🤖 自動生成されるもの

| 項目 | 内容 |
|---|---|
| SEOブログ記事 | タイトル・構成・導入・本文・まとめ（約3000字相当） |
| YouTube台本 | フック・ストーリー・教訓・CTA（4パート） |
| YouTube最適化 | タイトル案3つ・概要欄テキスト |
| アフィリエイト案 | Amazon商品リンク候補 |
| 内部リンク | 関連記事への自動リンク |
| SEO設定 | title・meta・OGP・構造化データ |

---

## 📅 推奨運用スケジュール

| 曜日 | 作業 | 所要時間 |
|---|---|---|
| 月曜 | テーマ決定＋記事生成＋push | 30分 |
| 水曜 | YouTube録画・編集・投稿 | 2〜3時間 |
| 金曜 | GSC/Analytics確認・次週テーマ選定 | 30分 |
| 週末 | コメント返信・改善 | 30分 |

---

## 💰 収益化ロードマップ

- **1〜2ヶ月**：20記事投稿。Googleインデックス開始
- **3〜4ヶ月**：50記事。アフィリエイト収益が発生し始める
- **5〜6ヶ月**：YouTube 1000人登録目標。月1〜3万円
- **7〜12ヶ月**：月5〜10万円の副収入として安定

---

## ❓ よくある質問

**Q: APIキーはどこで取得できますか？**
A: https://console.anthropic.com/ でアカウントを作成し、APIキーを発行してください。

**Q: 記事の文字数は？**
A: AI生成で約2000〜3000字の本文が生成されます。必要に応じて加筆してください。

**Q: デザインを変えたいです**
A: `docs/assets/css/style.css` を編集してください。CSSの知識があれば自由に変更できます。
