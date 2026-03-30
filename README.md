# 教養の教室 — 社会人教養ブログ 自動生成システム

## クイックスタート

```bash
pip install -r requirements.txt
cp .env.example .env   # APIキーを記入

# 記事1本生成
python scripts/generate.py "ソクラテスとは何者か" 哲学・思想

# 100本一括生成（約2〜3時間）
python scripts/generate.py --bulk

# カテゴリ指定で一括生成
python scripts/generate.py --bulk --category お金と資本
```

## 6テーマ構成
- お金と資本（17記事）
- 宗教（17記事）
- 哲学・思想（17記事）
- 歴史（17記事）
- 芸術（17記事）
- 言葉と文学（17記事）
= 合計102記事

## GitHubへの反映
```bash
git add . && git commit -m "add: 100記事一括追加" && git push
```
