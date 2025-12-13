# lovedoll

## スクレイピング → WordPress 連携スクリプト
`python scrape_to_wp.py` を使って、任意のカテゴリページから商品情報を取得し、WordPress REST API（`/wp-json/lovedoll/v1/add-item`）へ送信できます。
デフォルトの取得先は最新順の `https://yourdoll.jp/product-category/all-sex-dolls/?orderby=date` で、ページネーションは最大 10 ページまで辿ります。

`python scrape_happiness_to_wp.py` は `https://happiness-doll.com/products/list` をデフォルト取得元として同じ REST API に送信します（ページネーション上限 10 ページ、遅延 1.5 秒を挟んでロード待ちします）。happiness-doll 専用の HTML 構造（`li.ec-shelfGrid__item` 内の `.ec-shelfGrid__item-title`／`.ec-shelfGrid__item-image img`／`.discount-price`→`.price-flash`→`.price02`→`.price` の優先順）にのみ依存し、yourdoll.jp のセレクタは使用しません。
`python scrape_sweet_to_wp.py` は `https://sweet-doll.com/product-category/sedoll/` をデフォルト取得元として、`.product-grid-item` / `.product-image-link img` / `.wd-entities-title a` / `.price .woocommerce-Price-amount` に完全準拠した sweet-doll 専用パーサで抽出し、同 REST API に送信します（最大 10 ページのページネーション対応、重複 URL スキップ付き）。
`python scrape_kuma_to_wp.py` は `https://www.kuma-doll.com/Products/list-r1.html` をデフォルト取得元として、`.product-item` / `.image img` / `.title` / `.price span` に完全準拠した kuma-doll 専用パーサで抽出し、lazyload や `<noscript>` 内の画像・他の `<img>` もフォールバックで拾って同 REST API に送信します（最大 10 ページ、重複 URL スキップ・100 万円以上スキップ付き）。

### 必要ライブラリのインストール
```bash
pip install requests beautifulsoup4 lxml
```

### 実行例
```bash
python scrape_to_wp.py \
  --url "https://yourdoll.jp/product-category/all-sex-dolls/?orderby=date" \
  --wp-base "https://freya-era.com" \
  --limit 20 \
  --max-pages 10   # ページ数の上限を調整したい場合に指定（省略可）
```

`--wp-base` を省略した場合は `https://freya-era.com` を既定の送信先として利用します。
`--url` を省略すると `https://yourdoll.jp/product-category/all-sex-dolls/?orderby=date` を使用します。

```bash
# happiness-doll.com 向け（デフォルトURLは https://happiness-doll.com/products/list ）
python scrape_happiness_to_wp.py \
  --wp-base "https://freya-era.com" \
  --limit 20 \
  --max-pages 10 \
  --delay 1.5   # ページ取得後に待機したい秒数（ロード画面対策に変更可）

# sweet-doll.com 向け（デフォルトURLは https://sweet-doll.com/product-category/sedoll/ ）
python scrape_sweet_to_wp.py \
  --wp-base "https://freya-era.com" \
  --limit 20 \
  --max-pages 10

# kuma-doll.com 向け（デフォルトURLは https://www.kuma-doll.com/Products/list-r1.html ）
python scrape_kuma_to_wp.py \
  --wp-base "https://freya-era.com" \
  --limit 20 \
  --max-pages 10
```

### GitHub Actions での実行（手動トリガー）
`.github/workflows/scrape-and-post.yml` を手動実行（`workflow_dispatch`）すると、
入力されたカテゴリ URL・WordPress ベース URL（既定で `https://freya-era.com`）・任意の送信件数制限を使って
同じ処理を GitHub Actions 上で動かせます。必要に応じて Actions 画面から
パラメータを指定して実行してください。

`.github/workflows/scrape-happiness.yml` を手動実行すると、`scrape_happiness_to_wp.py` を使って
`https://happiness-doll.com/products/list`（入力で上書き可）をスクレイピングし、同様に WordPress へ登録できます。
`.github/workflows/scrape-sweet.yml` を手動実行すると、`scrape_sweet_to_wp.py` を使って
`https://sweet-doll.com/product-category/sedoll/`（入力で上書き可）をスクレイピングし、同様に WordPress へ登録できます。
`.github/workflows/scrape-kuma.yml` を手動実行すると、`scrape_kuma_to_wp.py` を使って
`https://www.kuma-doll.com/Products/list-r1.html`（入力で上書き可）をスクレイピングし、同様に WordPress へ登録できます。

### スクリプトの主な処理
- カテゴリページをスクレイピングし、ページネーションも自動で辿ります（1.5 秒の待機を標準で挟み、ロード画面を考慮）。
- 商品タイトル・価格・画像 URL・商品ページ URL を抽出し、価格を整数に正規化します（lazyload の `srcset` / `data-lazy-src` / `data-srcset` / `data-original` などや `<noscript>` 内の画像も考慮し、data: URI は除外）。
- 画像が取得できない商品や、価格が 100 万円以上の商品はスキップします。
- 相対 URL は絶対 URL へ変換します。
- すでに WordPress 側に存在する `product_url`（/wp-json/lovedoll/v1/list）や同一実行内で重複した商品 URL は POST をスキップします。
- WordPress REST API へ POST し、画像 URL と商品ページ URL（`product_url` として送信）を併せて送信、正常時はレスポンスの ID をログ出力します。
- HTTP エラーやタイムアウトをハンドリングします。

### WordPress 側の REST API / 画像ホットリンク対策
- `includes/lovedoll-products-api.php` で `/wp-json/lovedoll/v1/add-item` と `/wp-json/lovedoll/v1/list` を登録しています（`functions.php` 経由で読み込み）。
- 送信 JSON は `{ "title": "...", "price": 123456, "image_url": "https://...", "product_url": "https://..." }` 形式で、すべてのフィールドが必須です。
- `kuma-doll.com` ドメインの画像は WordPress サーバー側で `download_url()` → `media_handle_sideload()` でダウンロード・メディア登録し、取得したメディア URL を使ってホットリンク（ロゴ置換）を回避します。
- それ以外のドメイン画像も `media_sideload_image()` でメディア化し、投稿のアイキャッチに設定します。投稿には `product_url`・元画像 URL・最終的なメディア URL（`_final_image_url`）と価格がメタ保存されます。
