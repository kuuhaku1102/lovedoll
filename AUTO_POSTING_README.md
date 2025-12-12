# 毎日自動投稿機能 - 完全ガイド

## 概要

このシステムは、毎日10時に自動的に SEO 最適化されたブログ記事を生成し、WordPress に投稿します。キーワードが重複しないように管理し、全キーワードを網羅的にカバーします。

## 主要機能

### 1. キーワード管理システム
- **50種類以上のキーワード**を自動ローテーション
- **重複防止**：使用済みキーワードを追跡
- **自動リセット**：全キーワード使用後に自動的に新サイクル開始
- **進捗管理**：使用状況を JSON ファイルで永続化

### 2. 自動投稿スクリプト
- **毎日10時に自動実行**
- **AI による記事生成**：SEO 最適化されたコンテンツ
- **WordPress 自動投稿**：下書きまたは公開を選択可能
- **エラーハンドリング**：失敗時のログ記録

### 3. スケジュール管理
- **cron による定期実行**
- **ログ記録**：すべての実行履歴を保存
- **柔軟な設定**：時刻やステータスをカスタマイズ可能

## ファイル構成

```
lovedoll/
├── keyword_manager.py          # キーワード管理システム
├── auto_post_daily.py          # 自動投稿スクリプト
├── generate_seo_blog.py        # AI 記事生成スクリプト
├── setup_auto_posting.sh       # セットアップスクリプト
├── crontab.example             # cron 設定例
├── keyword_state.json          # キーワード使用状態（自動生成）
└── logs/                       # ログディレクトリ（自動生成）
    ├── auto_post_YYYYMMDD.log  # 日次ログ
    └── cron.log                # cron 実行ログ
```

## セットアップ

### 方法1: 自動セットアップ（推奨）

```bash
cd /path/to/lovedoll
./setup_auto_posting.sh
```

このスクリプトが以下を自動的に実行します：
1. Python と必要なパッケージの確認
2. 環境変数のチェック
3. ログディレクトリの作成
4. スクリプトのテスト実行
5. cron ジョブの設定

### 方法2: 手動セットアップ

#### ステップ1: 環境変数の設定

```bash
# 一時的に設定（現在のセッションのみ）
export AI_API="your-api-key-here"
export WP_BASE_URL="https://freya-era.com"
export POST_STATUS="publish"

# 永続的に設定（推奨）
echo 'export AI_API="your-api-key-here"' >> ~/.bashrc
echo 'export WP_BASE_URL="https://freya-era.com"' >> ~/.bashrc
echo 'export POST_STATUS="publish"' >> ~/.bashrc
source ~/.bashrc
```

#### ステップ2: 必要なパッケージのインストール

```bash
pip3 install requests openai
```

#### ステップ3: ログディレクトリの作成

```bash
mkdir -p logs
```

#### ステップ4: cron ジョブの設定

```bash
# crontab を編集
crontab -e

# 以下の行を追加（毎日10時に実行）
0 10 * * * cd /path/to/lovedoll && /usr/bin/python3 auto_post_daily.py --status publish >> logs/cron.log 2>&1
```

## 使用方法

### キーワード管理

#### 次のキーワードを確認

```bash
python3 keyword_manager.py --next
```

出力例：
```
Next keyword: ラブドール 選び方
```

#### 統計情報を表示

```bash
python3 keyword_manager.py --stats
```

出力例：
```
Keyword Statistics:
  Total Keywords: 50
  Used Keywords: 15
  Remaining Keywords: 35
  Current Cycle: 1
  Total Posts: 15
  Progress: 30.0%
  Last Updated: 2025-12-13T10:00:00
```

#### 残りのキーワード一覧

```bash
python3 keyword_manager.py --list
```

#### キーワードを使用済みにマーク

```bash
python3 keyword_manager.py --mark-used "ラブドール 選び方"
```

#### サイクルをリセット

```bash
python3 keyword_manager.py --reset
```

### 自動投稿

#### 通常実行（公開）

```bash
python3 auto_post_daily.py --status publish
```

#### 下書きとして保存

```bash
python3 auto_post_daily.py --status draft
```

#### ドライラン（実際には投稿しない）

```bash
python3 auto_post_daily.py --dry-run
```

#### 特定のキーワードで実行

```bash
python3 auto_post_daily.py --force-keyword "ラブドール おすすめ"
```

## キーワードデータベース

システムには以下の50種類以上のキーワードが登録されています：

### 基本・選び方（5種類）
1. ラブドール 選び方
2. ラブドール おすすめ
3. ラブドール 初心者
4. ラブドール 購入ガイド
5. ラブドール 比較

### メンテナンス・保管（5種類）
6. ラブドール メンテナンス
7. ラブドール 保管方法
8. ラブドール 手入れ
9. ラブドール 洗い方
10. ラブドール 収納

### 材質・種類（6種類）
11. ラブドール 価格
12. ラブドール 種類
13. ラブドール TPE シリコン 違い
14. ラブドール TPE
15. ラブドール シリコン
16. ラブドール 材質

### サイズ・重量（5種類）
17. ラブドール 軽量
18. ラブドール 小型
19. ラブドール サイズ
20. ラブドール 身長
21. ラブドール 重さ

### レビュー・評価（4種類）
22. ラブドール レビュー
23. ラブドール 口コミ
24. ラブドール 評判
25. ラブドール ランキング

### 購入・販売店（5種類）
26. ラブドール 通販
27. ラブドール 販売店
28. ラブドール 正規品
29. ラブドール 安全
30. ラブドール 匿名配送

### カスタマイズ（4種類）
31. ラブドール カスタマイズ
32. ラブドール 顔
33. ラブドール ウィッグ
34. ラブドール 衣装

### 用途別（5種類）
35. ラブドール 一人暮らし
36. ラブドール 初めて
37. ラブドール コスパ
38. ラブドール 高級
39. ラブドール リアル

### トラブル・Q&A（4種類）
40. ラブドール 失敗
41. ラブドール 注意点
42. ラブドール よくある質問
43. ラブドール トラブル

### その他（5種類）
44. ラブドール 寿命
45. ラブドール 修理
46. ラブドール 処分
47. ラブドール 保証
48. ラブドール アフターサービス

## スケジュール設定

### 毎日10時に自動投稿

```cron
0 10 * * * cd /path/to/lovedoll && /usr/bin/python3 auto_post_daily.py --status publish >> logs/cron.log 2>&1
```

### 毎週月曜日9時に統計レポート

```cron
0 9 * * 1 cd /path/to/lovedoll && /usr/bin/python3 keyword_manager.py --stats >> logs/stats.log 2>&1
```

### 毎月1日にサイクルリセット（オプション）

```cron
0 0 1 * * cd /path/to/lovedoll && /usr/bin/python3 keyword_manager.py --reset >> logs/reset.log 2>&1
```

## ログ管理

### ログファイルの場所

- **日次ログ**: `logs/auto_post_YYYYMMDD.log`
- **cron ログ**: `logs/cron.log`
- **統計ログ**: `logs/stats.log`

### ログの確認

```bash
# 最新の日次ログを表示
tail -f logs/auto_post_$(date +%Y%m%d).log

# cron ログを表示
tail -f logs/cron.log

# エラーのみを抽出
grep ERROR logs/auto_post_*.log
```

### ログのローテーション

古いログを定期的に削除することを推奨します：

```bash
# 30日以上前のログを削除
find logs/ -name "auto_post_*.log" -mtime +30 -delete
```

## トラブルシューティング

### AI_API が設定されていない

**症状：**
```
ERROR: AI_API environment variable is not set
```

**解決方法：**
```bash
export AI_API="your-api-key-here"
# または
echo 'export AI_API="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### cron ジョブが実行されない

**確認事項：**

1. cron が実行されているか確認
```bash
sudo systemctl status cron
```

2. crontab が正しく設定されているか確認
```bash
crontab -l
```

3. スクリプトのパスが正しいか確認
```bash
which python3
```

4. 環境変数が cron で利用可能か確認
```bash
# crontab の先頭に環境変数を追加
AI_API=your-api-key-here
WP_BASE_URL=https://freya-era.com
```

### WordPress への投稿が失敗する

**確認事項：**

1. WordPress URL が正しいか
2. REST API が有効か
3. ネットワーク接続が正常か
4. ログでエラー内容を確認

```bash
grep ERROR logs/auto_post_*.log
```

### キーワードが重複する

**原因：**
- `keyword_state.json` が破損している
- 手動でキーワードを指定している（`--force-keyword`）

**解決方法：**
```bash
# 状態ファイルを削除して再初期化
rm keyword_state.json
python3 keyword_manager.py --stats
```

## 運用のベストプラクティス

### 1. 定期的な監視

```bash
# 毎週月曜日に統計を確認
0 9 * * 1 cd /path/to/lovedoll && python3 keyword_manager.py --stats | mail -s "Weekly Blog Stats" your@email.com
```

### 2. ログのバックアップ

```bash
# 毎月1日にログをアーカイブ
0 0 1 * * cd /path/to/lovedoll && tar -czf logs_backup_$(date +%Y%m).tar.gz logs/
```

### 3. 記事の品質チェック

- 定期的に生成された記事を確認
- 必要に応じて手動で編集
- 読者のフィードバックを収集

### 4. キーワードの追加

新しいキーワードを追加する場合：

1. `keyword_manager.py` の `KEYWORD_DATABASE` リストを編集
2. 変更をコミット
3. システムが自動的に新しいキーワードを使用開始

## セキュリティ

### 環境変数の保護

```bash
# .bashrc のパーミッションを制限
chmod 600 ~/.bashrc

# API キーを環境変数ファイルに保存
echo 'AI_API=your-api-key' > ~/.env_lovedoll
chmod 600 ~/.env_lovedoll

# crontab で読み込み
0 10 * * * source ~/.env_lovedoll && cd /path/to/lovedoll && python3 auto_post_daily.py
```

### ログファイルの保護

```bash
# ログディレクトリのパーミッションを制限
chmod 700 logs/
```

## パフォーマンス

### 実行時間

- **記事生成**: 30-60秒（AI API のレスポンス時間に依存）
- **WordPress 投稿**: 5-10秒
- **合計**: 約1分

### リソース使用量

- **CPU**: 低（AI API 呼び出し時のみ）
- **メモリ**: 50-100MB
- **ディスク**: ログファイルのみ（1日あたり約1MB）

## カスタマイズ

### 投稿時刻の変更

```bash
# 毎日15時に変更
0 15 * * * cd /path/to/lovedoll && python3 auto_post_daily.py --status publish >> logs/cron.log 2>&1
```

### 週末のみ投稿

```bash
# 土曜日と日曜日の10時
0 10 * * 6,0 cd /path/to/lovedoll && python3 auto_post_daily.py --status publish >> logs/cron.log 2>&1
```

### 1日に複数回投稿

```bash
# 10時と15時に投稿
0 10,15 * * * cd /path/to/lovedoll && python3 auto_post_daily.py --status publish >> logs/cron.log 2>&1
```

## まとめ

この自動投稿システムにより、以下が実現されます：

✅ **毎日10時に自動投稿**
✅ **50種類以上のキーワードを網羅**
✅ **キーワードの重複を完全防止**
✅ **SEO 最適化されたコンテンツ**
✅ **完全自動化された運用**
✅ **詳細なログ記録**
✅ **柔軟なカスタマイズ**

これにより、手間をかけずに継続的に高品質なコンテンツを公開し、SEO 効果を最大化できます。
