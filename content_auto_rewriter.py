#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
コンテンツ自動リライトシステム
低パフォーマンスの記事を自動検出し、AI がリライトして改善
"""

import os
import json
import requests
from datetime import datetime
from openai import OpenAI

class ContentAutoRewriter:
    def __init__(self):
        self.site_url = os.getenv('WP_SITE_URL')
        self.wp_user = os.getenv('WP_USER')
        self.wp_password = os.getenv('WP_APP_PASSWORD')
        
        # OpenAI クライアント
        self.client = OpenAI()
        
        # データファイルのパス
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.history_file = os.path.join(self.data_dir, 'rewrite_history.json')
        self.analytics_file = os.path.join(self.data_dir, 'analytics_data.json')
        
        # ログファイル
        self.log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.log_file = os.path.join(self.log_dir, 'rewrite.log')
    
    def log(self, message):
        """ログを記録"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def load_history(self):
        """リライト履歴を読み込み"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_history(self, history):
        """リライト履歴を保存"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def simulate_analytics_data(self, posts):
        """アナリティクスデータをシミュレート（実際はGoogle Analytics APIを使用）"""
        self.log("アナリティクスデータを生成中...")
        
        import random
        
        analytics_data = {}
        for post in posts:
            post_id = post['id']
            post_title = post['title']['rendered']
            
            # ランダムにパフォーマンスデータを生成
            pageviews = random.randint(10, 500)
            avg_time_on_page = random.randint(15, 180)
            bounce_rate = random.randint(40, 95)
            
            analytics_data[str(post_id)] = {
                'post_title': post_title,
                'pageviews': pageviews,
                'avg_time_on_page': avg_time_on_page,
                'bounce_rate': bounce_rate,
                'last_updated': datetime.now().isoformat()
            }
        
        # データを保存
        with open(self.analytics_file, 'w', encoding='utf-8') as f:
            json.dump(analytics_data, f, ensure_ascii=False, indent=2)
        
        self.log(f"✓ {len(analytics_data)}件のアナリティクスデータを生成しました")
        
        return analytics_data
    
    def detect_low_performance_posts(self, analytics_data):
        """低パフォーマンス記事を検出"""
        self.log("低パフォーマンス記事を検出中...")
        
        low_performance_posts = []
        
        for post_id, data in analytics_data.items():
            pageviews = data['pageviews']
            avg_time = data['avg_time_on_page']
            bounce_rate = data['bounce_rate']
            
            # 低パフォーマンスの基準
            is_low_performance = (
                pageviews < 100 or
                avg_time < 30 or
                bounce_rate > 80
            )
            
            if is_low_performance:
                # パフォーマンススコアを計算（低いほど優先度が高い）
                performance_score = (pageviews / 10) + avg_time - bounce_rate
                
                low_performance_posts.append({
                    'post_id': int(post_id),
                    'post_title': data['post_title'],
                    'pageviews': pageviews,
                    'avg_time_on_page': avg_time,
                    'bounce_rate': bounce_rate,
                    'performance_score': performance_score
                })
        
        # パフォーマンススコアが低い順にソート
        low_performance_posts.sort(key=lambda x: x['performance_score'])
        
        self.log(f"✓ {len(low_performance_posts)}件の低パフォーマンス記事を検出しました")
        
        return low_performance_posts
    
    def rewrite_introduction(self, post_title, post_content):
        """導入文をリライト"""
        self.log("  導入文をリライト中...")
        
        prompt = f"""あなたはコンテンツライターの専門家です。以下の記事の導入文を改善してください。

【記事タイトル】
{post_title}

【現在の導入文】
{post_content[:500]}

【改善の指針】
1. 読者の悩みを明確にする
2. この記事で分かることを箇条書きで提示
3. 読み切りメリットを強調
4. 親しみやすく、読みやすい文体
5. ラブドールを「美術品」「工芸品」として扱う表現を維持

【出力形式】
改善された導入文のみを出力してください。HTML タグは不要です。
"""
        
        response = self.client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        rewritten_intro = response.choices[0].message.content.strip()
        
        self.log(f"    ✓ 導入文をリライトしました")
        
        return rewritten_intro
    
    def improve_content_structure(self, post_content):
        """本文の構造を改善"""
        self.log("  本文の構造を改善中...")
        
        prompt = f"""あなたはコンテンツライターの専門家です。以下の記事本文を改善してください。

【現在の本文】
{post_content}

【改善の指針】
1. 冗長な表現を削除
2. 具体例を追加
3. 箇条書きで読みやすく
4. 見出しを論理的に再構成
5. ラブドールを「美術品」「工芸品」として扱う表現を維持
6. 性的な表現は一切含めない

【出力形式】
改善された本文のみを出力してください。Markdown 形式で出力してください。
"""
        
        response = self.client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        improved_content = response.choices[0].message.content.strip()
        
        self.log(f"    ✓ 本文の構造を改善しました")
        
        return improved_content
    
    def improve_conclusion(self, post_title, post_content):
        """まとめを改善"""
        self.log("  まとめを改善中...")
        
        prompt = f"""あなたはコンテンツライターの専門家です。以下の記事のまとめを改善してください。

【記事タイトル】
{post_title}

【記事の内容（抜粋）】
{post_content[:1000]}

【改善の指針】
1. 結論を明確に
2. 次の行動を提示（CTA）
3. 読者のベネフィットを強調
4. 親しみやすく、前向きな文体
5. ラブドールを「美術品」「工芸品」として扱う表現を維持

【出力形式】
改善されたまとめのみを出力してください。HTML タグは不要です。
"""
        
        response = self.client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        improved_conclusion = response.choices[0].message.content.strip()
        
        self.log(f"    ✓ まとめを改善しました")
        
        return improved_conclusion
    
    def update_wordpress_post(self, post_id, content):
        """WordPress の記事を更新"""
        self.log(f"  WordPress に変更を反映中...")
        
        url = f"{self.site_url}/wp-json/wp/v2/posts/{post_id}"
        
        auth = (self.wp_user, self.wp_password)
        headers = {'Content-Type': 'application/json'}
        
        updates = {'content': content}
        
        response = requests.post(url, json=updates, auth=auth, headers=headers)
        
        if response.status_code == 200:
            self.log(f"    ✓ 記事を更新しました（ID: {post_id}）")
            return True
        else:
            self.log(f"    ✗ 記事の更新に失敗しました: {response.status_code}")
            return False
    
    def rewrite_post(self, post_info):
        """記事をリライト"""
        post_id = post_info['post_id']
        post_title = post_info['post_title']
        
        self.log(f"\n[記事リライト] ID: {post_id}, タイトル: {post_title}")
        self.log(f"  パフォーマンス: PV={post_info['pageviews']}, 滞在時間={post_info['avg_time_on_page']}秒, 直帰率={post_info['bounce_rate']}%")
        
        # WordPress から記事の詳細を取得
        url = f"{self.site_url}/wp-json/wp/v2/posts/{post_id}"
        response = requests.get(url)
        
        if response.status_code != 200:
            self.log(f"  ✗ 記事の取得に失敗しました")
            return None
        
        post = response.json()
        post_content = post['content']['rendered']
        
        # 導入文をリライト
        rewritten_intro = self.rewrite_introduction(post_title, post_content)
        
        # 本文の構造を改善
        improved_content = self.improve_content_structure(post_content)
        
        # まとめを改善
        improved_conclusion = self.improve_conclusion(post_title, post_content)
        
        # 新しいコンテンツを構築
        new_content = f"{rewritten_intro}\n\n{improved_content}\n\n{improved_conclusion}"
        
        # WordPress を更新
        success = self.update_wordpress_post(post_id, new_content)
        
        if success:
            # リライト履歴を記録
            rewrite_record = {
                'post_id': post_id,
                'post_title': post_title,
                'rewrite_date': datetime.now().isoformat(),
                'before_metrics': {
                    'pageviews': post_info['pageviews'],
                    'avg_time_on_page': post_info['avg_time_on_page'],
                    'bounce_rate': post_info['bounce_rate']
                },
                'improvements': [
                    '導入文を読者の悩みに焦点',
                    '本文の構造を改善',
                    'まとめにCTAを追加'
                ],
                'after_metrics': {
                    'pageviews': None,
                    'avg_time_on_page': None,
                    'bounce_rate': None
                }
            }
            
            return rewrite_record
        
        return None
    
    def run(self, max_rewrites=5):
        """コンテンツ自動リライトを実行"""
        self.log("\n" + "="*60)
        self.log("コンテンツ自動リライトシステム 開始")
        self.log("="*60)
        
        # WordPress から記事を取得
        url = f"{self.site_url}/wp-json/wp/v2/posts"
        params = {'per_page': 100, 'status': 'publish'}
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            self.log("✗ 記事の取得に失敗しました")
            return
        
        posts = response.json()
        
        if not posts:
            self.log("✗ 記事が見つかりませんでした")
            return
        
        self.log(f"✓ {len(posts)}件の記事を取得しました")
        
        # アナリティクスデータを取得（シミュレート）
        analytics_data = self.simulate_analytics_data(posts)
        
        # 低パフォーマンス記事を検出
        low_performance_posts = self.detect_low_performance_posts(analytics_data)
        
        if not low_performance_posts:
            self.log("✓ 低パフォーマンスの記事はありませんでした")
            return
        
        # リライト履歴を読み込み
        history = self.load_history()
        
        # 最大N件までリライト
        rewritten_count = 0
        for post_info in low_performance_posts[:max_rewrites]:
            rewrite_record = self.rewrite_post(post_info)
            
            if rewrite_record:
                history.append(rewrite_record)
                rewritten_count += 1
        
        # リライト履歴を保存
        self.save_history(history)
        
        self.log("\n" + "="*60)
        self.log(f"コンテンツ自動リライトシステム 完了: {rewritten_count}件の記事をリライトしました")
        self.log("="*60)


if __name__ == '__main__':
    rewriter = ContentAutoRewriter()
    rewriter.run(max_rewrites=5)
