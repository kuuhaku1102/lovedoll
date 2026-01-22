# GitHub Actions ワークフロー更新手順

## 概要

GitHub App の権限制限により、ワークフローファイルは手動で更新する必要があります。以下の手順に従って、`.github/workflows/daily-auto-post.yml` を更新してください。

---

## 更新手順

### ステップ1: GitHub リポジトリにアクセス

1. https://github.com/kuuhaku1102/lovedoll にアクセス
2. `.github/workflows/daily-auto-post.yml` ファイルを開く

### ステップ2: ファイルを編集

右上の鉛筆アイコン（Edit this file）をクリックして編集モードに入ります。

### ステップ3: スクリプト実行部分を変更

以下の部分を見つけて変更してください。

**変更前**

```yaml
      - name: Run auto post script
        env:
          AI_API: ${{ secrets.AI_API }}
          WP_BASE_URL: ${{ secrets.WP_SITE_URL }}
          POST_STATUS: publish
        run: |
          python auto_post_daily.py --status publish
```

**変更後**

```yaml
      - name: Run SEO blog generation (v3.0 - 6 Steps)
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          WP_SITE_URL: ${{ secrets.WP_SITE_URL }}
          WP_USER: ${{ secrets.WP_USER }}
          WP_APP_PASSWORD: ${{ secrets.WP_APP_PASSWORD }}
        run: |
          python auto_blog_v3.py
```

### ステップ4: コミット部分を変更

以下の部分を見つけて変更してください。

**変更前**

```yaml
      - name: Commit and push keyword state
        if: success()
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          
          # Add keyword state file
          git add keyword_state.json || true
          
          # Check if there are changes to commit
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "Update keyword state after auto-posting [skip ci]"
            
            # Push with retry logic
            for i in {1..3}; do
              if git push origin main; then
                echo "Successfully pushed changes"
                break
              else
                echo "Push failed, retrying in 5 seconds..."
                sleep 5
                git pull --rebase origin main || true
              fi
            done
          fi
```

**変更後**

```yaml
      - name: Commit and push article data
        if: success()
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          
          # Add article data and history
          git add data/ seo_category_design.json || true
          
          # Check if there are changes to commit
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "Auto: ラブドールSEO記事生成 v3.0 [$(date +'%Y-%m-%d %H:%M:%S')]"
            
            # Push with retry logic
            for i in {1..3}; do
              if git push origin main; then
                echo "Successfully pushed changes"
                break
              else
                echo "Push failed, retrying in 5 seconds..."
                sleep 5
                git pull --rebase origin main || true
              fi
            done
          fi
```

### ステップ5: 変更をコミット

1. 「Commit changes...」ボタンをクリック
2. コミットメッセージを入力（例：「Update workflow to use SEO v3.0 scripts」）
3. 「Commit changes」をクリック

---

## 完全なワークフローファイル（参考）

以下は、更新後の完全なワークフローファイルです。参考にしてください。

```yaml
name: Daily Auto Post

on:
  schedule:
    # 毎日 JST 10:00 (UTC 01:00) に実行
    - cron: '0 1 * * *'
  workflow_dispatch:  # 手動実行も可能

permissions:
  contents: write  # article_history.json をコミット・プッシュするために必要

jobs:
  auto-post:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install requests openai
      
      - name: Create logs directory
        run: mkdir -p logs
      
      - name: Pull latest changes
        run: |
          git pull origin main || true
      
      - name: Run SEO blog generation (v3.0 - 6 Steps)
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          WP_SITE_URL: ${{ secrets.WP_SITE_URL }}
          WP_USER: ${{ secrets.WP_USER }}
          WP_APP_PASSWORD: ${{ secrets.WP_APP_PASSWORD }}
        run: |
          python auto_blog_v3.py
      
      - name: Upload logs
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: auto-post-logs-${{ github.run_number }}
          path: logs/
          retention-days: 30
      
      - name: Commit and push article data
        if: success()
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          
          # Add article data and history
          git add data/ seo_category_design.json || true
          
          # Check if there are changes to commit
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "Auto: ラブドールSEO記事生成 v3.0 [$(date +'%Y-%m-%d %H:%M:%S')]"
            
            # Push with retry logic
            for i in {1..3}; do
              if git push origin main; then
                echo "Successfully pushed changes"
                break
              else
                echo "Push failed, retrying in 5 seconds..."
                sleep 5
                git pull --rebase origin main || true
              fi
            done
          fi
```

---

## GitHub Secrets の確認

ワークフローが正しく動作するために、以下の4つのシークレットが設定されているか確認してください。

1. **OPENAI_API_KEY**: Gemini API キー（OpenAI互換APIとして使用）
2. **WP_SITE_URL**: WordPress サイトのURL（例：`https://freya-era.com`）
3. **WP_USER**: WordPress の管理者ユーザー名
4. **WP_APP_PASSWORD**: WordPress アプリケーションパスワード

### 確認方法

1. GitHub リポジトリの「Settings」タブをクリック
2. 左側メニューの「Secrets and variables」→「Actions」をクリック
3. 4つのシークレットがすべて表示されているか確認

### 不足している場合

「New repository secret」ボタンをクリックして、不足しているシークレットを追加してください。

---

## 手動実行でテスト

ワークフローを更新したら、手動実行でテストしてください。

1. GitHub リポジトリの「Actions」タブをクリック
2. 左側の「Daily Auto Post」をクリック
3. 右側の「Run workflow」ボタンをクリック
4. 「Run workflow」を再度クリックして実行

実行が完了したら、以下を確認してください。

- ✅ ワークフローが正常に完了したか
- ✅ WordPress に新しい記事が投稿されたか
- ✅ 記事の内容にコンテンツポリシー違反がないか

---

## トラブルシューティング

### エラー: `ModuleNotFoundError: No module named 'openai'`

**原因**: OpenAI ライブラリがインストールされていない

**解決方法**: ワークフローの「Install dependencies」ステップで `openai` がインストールされているか確認してください。

### エラー: `FileNotFoundError: [Errno 2] No such file or directory: 'seo_category_design.json'`

**原因**: SEO カテゴリー設計ファイルが見つからない

**解決方法**: リポジトリのルートディレクトリに `seo_category_design.json` が存在するか確認してください。

### エラー: `Unauthorized`

**原因**: WordPress アプリケーションパスワードが間違っている

**解決方法**: WordPress 管理画面でアプリケーションパスワードを再生成し、GitHub Secrets を更新してください。

---

## 更新完了後の確認事項

- ✅ ワークフローファイルが正しく更新されたか
- ✅ GitHub Secrets が正しく設定されているか
- ✅ 手動実行でテストが成功したか
- ✅ 生成された記事にコンテンツポリシー違反がないか

---

**更新日**: 2026年1月23日  
**バージョン**: 3.0  
**実装者**: Manus AI Agent
