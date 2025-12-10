# lovedoll

## スクレイピング → WordPress 連携スクリプト
`python scrape_to_wp.py` を使って、任意のカテゴリページから商品情報を取得し、WordPress REST API（`/wp-json/lovedoll/v1/add-item`）へ送信できます。

### 必要ライブラリのインストール
```bash
pip install requests beautifulsoup4 lxml
```

### 実行例
```bash
python scrape_to_wp.py \
  --url "https://yourdoll.jp/product-category/all-sex-dolls/" \
  --wp-base "https://example.com" \
  --limit 20   # 送信数を制限したい場合に指定（省略可）
```

### GitHub Actions での実行（手動トリガー）
`.github/workflows/scrape-and-post.yml` を手動実行（`workflow_dispatch`）すると、
入力されたカテゴリ URL・WordPress ベース URL・任意の送信件数制限を使って
同じ処理を GitHub Actions 上で動かせます。必要に応じて Actions 画面から
パラメータを指定して実行してください。

### スクリプトの主な処理
- カテゴリページをスクレイピングし、ページネーションも自動で辿ります。
- 商品タイトル・価格・画像 URL を抽出し、価格を整数に正規化します。
- 相対 URL は絶対 URL へ変換します。
- WordPress REST API へ POST し、正常時はレスポンスの ID をログ出力します。
- HTTP エラーやタイムアウトをハンドリングします。
