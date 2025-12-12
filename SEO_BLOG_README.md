# SEO ブログ自動生成機能

## 概要

このスクリプトは、環境変数 `AI_API` を使用して、lovedoll 系のキーワードで SEO を考慮したブログ記事を自動生成し、WordPress に投稿する機能を提供します。

## 機能

### 主要機能

1. **AI による記事生成**
   - OpenAI 互換 API を使用した高品質な記事生成
   - SEO 最適化されたコンテンツ構造
   - キーワード密度の自動調整

2. **SEO 最適化**
   - タイトルタグの最適化（30-40文字）
   - メタディスクリプションの自動生成（120-160文字）
   - 適切な見出し構造（H2, H3）
   - キーワードの自然な配置

3. **WordPress 統合**
   - カスタム REST API エンドポイント
   - 自動タグ付け
   - AI 生成フラグの管理
   - 管理画面での識別表示

## セットアップ

### 1. 環境変数の設定

```bash
export AI_API="your-api-key-here"
```

画像に表示されている `AT_API` という環境変数名の場合は、以下のように設定してください：

```bash
export AI_API="$AT_API"
```

### 2. 必要なパッケージのインストール

```bash
pip install requests openai
```

### 3. WordPress テーマの有効化

functions.php に以下が含まれていることを確認してください：

```php
require_once get_template_directory() . '/includes/seo-blog-api.php';
```

## 使用方法

### 基本的な使い方

```bash
# デフォルトキーワードで記事生成（下書き保存）
python generate_seo_blog.py

# キーワードを指定して記事生成
python generate_seo_blog.py --keyword "ラブドール 選び方"

# 記事を公開状態で投稿
python generate_seo_blog.py --keyword "ラブドール おすすめ" --status publish

# WordPress URL を指定
python generate_seo_blog.py --keyword "ラブドール 初心者" --wp-base "https://your-site.com"
```

### 利用可能なキーワードテンプレートの確認

```bash
python generate_seo_blog.py --list-keywords
```

出力例：
```
Available keyword templates:
  1. ラブドール 選び方
  2. ラブドール おすすめ
  3. ラブドール 初心者
  4. ラブドール メンテナンス
  5. ラブドール 保管方法
  6. ラブドール 価格
  7. ラブドール 種類
  8. ラブドール TPE シリコン 違い
  9. ラブドール 購入ガイド
  10. ラブドール レビュー
```

## コマンドラインオプション

| オプション | 説明 | デフォルト値 |
|-----------|------|-------------|
| `--keyword` | ターゲットキーワード | "ラブドール 選び方" |
| `--wp-base` | WordPress のベース URL | "https://freya-era.com" |
| `--status` | 投稿ステータス（draft/publish） | "draft" |
| `--list-keywords` | キーワードテンプレート一覧を表示 | - |

## 生成される記事の構造

### 1. タイトル
- キーワードを含む魅力的なタイトル
- 30-40文字で最適化

### 2. メタディスクリプション
- 検索結果に表示される説明文
- 120-160文字で最適化

### 3. 本文
- 2000-3000文字の詳細な記事
- 適切な見出し構造（H2, H3）
- キーワード密度: 1-2%
- E-E-A-T を意識した内容

### 4. 記事構成
- **導入**: 問題提起・共感
- **本論**: 具体的な解決策・ノウハウ
- **まとめ**: 行動喚起

### 5. タグ
- 関連する5-7個のタグを自動生成

## WordPress API エンドポイント

### 記事作成

**エンドポイント**: `/wp-json/lovedoll/v1/create-blog-post`

**メソッド**: POST

**リクエストボディ**:
```json
{
  "title": "記事タイトル",
  "content": "記事本文（HTML）",
  "status": "draft",
  "excerpt": "抜粋",
  "meta_description": "メタディスクリプション",
  "tags": ["タグ1", "タグ2"],
  "keyword": "ターゲットキーワード"
}
```

**レスポンス**:
```json
{
  "success": true,
  "post_id": 123,
  "permalink": "https://example.com/post-url",
  "title": "記事タイトル",
  "status": "draft"
}
```

### AI 生成記事の一覧取得

**エンドポイント**: `/wp-json/lovedoll/v1/blog-posts`

**メソッド**: GET

**パラメータ**:
- `per_page`: 1ページあたりの記事数（デフォルト: 10）
- `page`: ページ番号（デフォルト: 1）

**レスポンス**:
```json
{
  "posts": [
    {
      "id": 123,
      "title": "記事タイトル",
      "excerpt": "抜粋",
      "permalink": "https://example.com/post-url",
      "date": "2025-12-13T12:00:00+09:00",
      "status": "publish",
      "target_keyword": "ラブドール 選び方",
      "ai_generated_date": "2025-12-13 12:00:00"
    }
  ],
  "total": 50,
  "total_pages": 5
}
```

## WordPress 管理画面

### AI 生成記事の識別

投稿一覧画面に「AI Generated」列が追加され、以下の情報が表示されます：

- ✓ AI: AI で生成された記事
- ターゲットキーワード（小さく表示）

### カスタムフィールド

各 AI 生成記事には以下のカスタムフィールドが保存されます：

- `_ai_generated`: AI 生成フラグ（true）
- `_ai_generated_date`: 生成日時
- `_target_keyword`: ターゲットキーワード
- `_yoast_wpseo_metadesc`: メタディスクリプション（Yoast SEO 対応）

## SEO ベストプラクティス

### 1. キーワード選定
- ロングテールキーワードを優先
- 検索意図を明確にする
- 競合分析を実施

### 2. コンテンツ品質
- オリジナリティの確保
- 読者に価値を提供
- 専門性・権威性・信頼性（E-E-A-T）

### 3. 技術的 SEO
- 適切な見出し構造
- メタタグの最適化
- 内部リンクの活用

### 4. ユーザー体験
- 読みやすい文章
- 適切な段落分け
- 視覚的な要素の追加

## トラブルシューティング

### AI_API が設定されていない

**エラー**: `AI_API environment variable is not set`

**解決方法**:
```bash
export AI_API="your-api-key-here"
```

### WordPress への接続エラー

**エラー**: `Failed to publish post: Connection error`

**解決方法**:
1. WordPress URL が正しいか確認
2. REST API が有効になっているか確認
3. ファイアウォール設定を確認

### JSON パースエラー

**エラー**: `Failed to parse JSON response`

**解決方法**:
- AI の応答が不完全な場合、自動的にフォールバック処理が実行されます
- ログを確認して AI の応答内容をチェック

## 自動化

### cron での定期実行

```bash
# 毎日午前9時に記事を生成
0 9 * * * cd /path/to/lovedoll && /usr/bin/python3 generate_seo_blog.py --keyword "ラブドール おすすめ" --status publish
```

### 複数キーワードの一括処理

```bash
#!/bin/bash
keywords=(
  "ラブドール 選び方"
  "ラブドール おすすめ"
  "ラブドール 初心者"
)

for keyword in "${keywords[@]}"; do
  python generate_seo_blog.py --keyword "$keyword" --status draft
  sleep 60  # API レート制限対策
done
```

## セキュリティ

### 本番環境での注意事項

1. **API 認証の追加**
   - `permission_callback` を適切に設定
   - WordPress ユーザー認証を実装

2. **環境変数の保護**
   - `.env` ファイルを使用
   - Git にコミットしない

3. **入力検証**
   - すべての入力をサニタイズ
   - XSS 対策を実施

## ライセンス

このスクリプトは lovedoll テーマの一部として提供されます。

## サポート

問題が発生した場合は、以下を確認してください：

1. 環境変数が正しく設定されているか
2. WordPress REST API が有効か
3. 必要なパッケージがインストールされているか
4. ログファイルでエラー内容を確認

## 更新履歴

### v1.0.0 (2025-12-13)
- 初回リリース
- AI による記事生成機能
- WordPress 統合
- SEO 最適化
