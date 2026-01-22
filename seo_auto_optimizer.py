#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEO 自動最適化エンジン
検索順位を自動監視し、順位が低下した記事を自動的に最適化
"""

import os
import json
import requests
from datetime import datetime, timedelta
from openai import OpenAI

class SEOAutoOptimizer:
    def __init__(self):
        self.site_url = os.getenv('WP_SITE_URL')
        self.wp_user = os.getenv('WP_USER')
        self.wp_password = os.getenv('WP_APP_PASSWORD')
        
        # OpenAI クライアント
        self.client = OpenAI()
        
        # データファイルのパス
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.history_file = os.path.join(self.data_dir, 'seo_optimization_history.json')
        self.rank_data_file = os.path.join(self.data_dir, 'search_rank_data.json')
        
        # ログファイル
        self.log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.log_file = os.path.join(self.log_dir, 'seo_optimization.log')
    
    def log(self, message):
        """ログを記録"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def load_history(self):
        """最適化履歴を読み込み"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_history(self, history):
        """最適化履歴を保存"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def load_rank_data(self):
        """検索順位データを読み込み"""
        if os.path.exists(self.rank_data_file):
            with open(self.rank_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_rank_data(self, rank_data):
        """検索順位データを保存"""
        with open(self.rank_data_file, 'w', encoding='utf-8') as f:
            json.dump(rank_data, f, ensure_ascii=False, indent=2)
    
    def fetch_wordpress_posts(self):
        """WordPress から全記事を取得"""
        self.log("WordPress から記事を取得中...")
        
        posts = []
        page = 1
        per_page = 100
        
        while True:
            url = f"{self.site_url}/wp-json/wp/v2/posts"
            params = {
                'page': page,
                'per_page': per_page,
                'status': 'publish'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                break
            
            batch = response.json()
            if not batch:
                break
            
            posts.extend(batch)
            page += 1
        
        self.log(f"✓ {len(posts)}件の記事を取得しました")
        return posts
    
    def simulate_search_rank_data(self, posts):
        """検索順位データをシミュレート（実際はGoogle Search Console APIを使用）"""
        self.log("検索順位データを生成中...")
        
        import random
        
        rank_data = {}
        for post in posts:
            post_id = post['id']
            post_title = post['title']['rendered']
            
            # 前回の順位を取得
            prev_rank_data = self.load_rank_data()
            prev_rank = prev_rank_data.get(str(post_id), {}).get('rank', random.randint(5, 30))
            
            # 今回の順位をシミュレート（前回から±10の範囲でランダムに変動）
            current_rank = max(1, prev_rank + random.randint(-10, 10))
            
            rank_data[str(post_id)] = {
                'post_title': post_title,
                'rank': current_rank,
                'prev_rank': prev_rank,
                'rank_change': current_rank - prev_rank,
                'last_updated': datetime.now().isoformat()
            }
        
        self.save_rank_data(rank_data)
        self.log(f"✓ {len(rank_data)}件の検索順位データを生成しました")
        
        return rank_data
    
    def detect_rank_drop_posts(self, rank_data, threshold=5):
        """順位が低下した記事を検出"""
        self.log(f"順位が{threshold}位以上低下した記事を検出中...")
        
        drop_posts = []
        for post_id, data in rank_data.items():
            rank_change = data['rank_change']
            
            # 順位が低下（数値が増加）した場合
            if rank_change >= threshold:
                drop_posts.append({
                    'post_id': int(post_id),
                    'post_title': data['post_title'],
                    'prev_rank': data['prev_rank'],
                    'current_rank': data['rank'],
                    'rank_drop': rank_change
                })
        
        # 順位低下が大きい順にソート
        drop_posts.sort(key=lambda x: x['rank_drop'], reverse=True)
        
        self.log(f"✓ {len(drop_posts)}件の順位低下記事を検出しました")
        
        return drop_posts
    
    def optimize_title(self, current_title, post_content):
        """タイトルを最適化"""
        self.log(f"  タイトルを最適化中: {current_title}")
        
        prompt = f"""あなたは SEO の専門家です。以下の記事タイトルを最適化してください。

【現在のタイトル】
{current_title}

【記事の内容（抜粋）】
{post_content[:500]}

【最適化の指針】
1. 検索意図に合ったタイトルにする
2. クリック率を高めるパワーワードを追加（例：完全ガイド、徹底解説、2026年最新）
3. 文字数を30〜40文字に最適化
4. 数字を使って具体性を向上（例：5つの方法、3ステップ）
5. ラブドールを「美術品」「工芸品」として扱う表現を維持

【出力形式】
最適化されたタイトルのみを出力してください。説明は不要です。
"""
        
        response = self.client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        optimized_title = response.choices[0].message.content.strip()
        
        self.log(f"    → 最適化後: {optimized_title}")
        
        return optimized_title
    
    def optimize_meta_description(self, post_title, post_content):
        """メタディスクリプションを最適化"""
        self.log(f"  メタディスクリプションを最適化中...")
        
        prompt = f"""あなたは SEO の専門家です。以下の記事のメタディスクリプションを最適化してください。

【記事タイトル】
{post_title}

【記事の内容（抜粋）】
{post_content[:500]}

【最適化の指針】
1. 検索結果での表示を最適化
2. CTA を含む魅力的な説明文にする
3. 文字数を120〜160文字に最適化
4. 読者のベネフィットを明確に
5. ラブドールを「美術品」「工芸品」として扱う表現を維持

【出力形式】
最適化されたメタディスクリプションのみを出力してください。説明は不要です。
"""
        
        response = self.client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        optimized_meta = response.choices[0].message.content.strip()
        
        self.log(f"    → メタディスクリプション: {optimized_meta[:50]}...")
        
        return optimized_meta
    
    def update_wordpress_post(self, post_id, updates):
        """WordPress の記事を更新"""
        self.log(f"  WordPress に変更を反映中...")
        
        url = f"{self.site_url}/wp-json/wp/v2/posts/{post_id}"
        
        auth = (self.wp_user, self.wp_password)
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, json=updates, auth=auth, headers=headers)
        
        if response.status_code == 200:
            self.log(f"    ✓ 記事を更新しました（ID: {post_id}）")
            return True
        else:
            self.log(f"    ✗ 記事の更新に失敗しました: {response.status_code}")
            return False
    
    def optimize_post(self, post_id, post_title, rank_info):
        """記事を最適化"""
        self.log(f"\n[記事最適化] ID: {post_id}, タイトル: {post_title}")
        self.log(f"  順位変動: {rank_info['prev_rank']}位 → {rank_info['current_rank']}位 ({rank_info['rank_drop']}位低下)")
        
        # WordPress から記事の詳細を取得
        url = f"{self.site_url}/wp-json/wp/v2/posts/{post_id}"
        response = requests.get(url)
        
        if response.status_code != 200:
            self.log(f"  ✗ 記事の取得に失敗しました")
            return None
        
        post = response.json()
        post_content = post['content']['rendered']
        
        # タイトルを最適化
        optimized_title = self.optimize_title(post_title, post_content)
        
        # メタディスクリプションを最適化
        optimized_meta = self.optimize_meta_description(optimized_title, post_content)
        
        # WordPress を更新
        updates = {
            'title': optimized_title,
            'meta': {
                'description': optimized_meta
            }
        }
        
        success = self.update_wordpress_post(post_id, updates)
        
        if success:
            # 最適化履歴を記録
            optimization_record = {
                'post_id': post_id,
                'post_title': post_title,
                'optimization_date': datetime.now().isoformat(),
                'before': {
                    'rank': rank_info['prev_rank'],
                    'title': post_title,
                    'meta_description': post.get('meta', {}).get('description', '')
                },
                'after': {
                    'rank': rank_info['current_rank'],
                    'title': optimized_title,
                    'meta_description': optimized_meta
                },
                'improvements': [
                    'タイトルにパワーワード追加',
                    'メタディスクリプションにCTA追加',
                    '文字数を最適化'
                ]
            }
            
            return optimization_record
        
        return None
    
    def run(self, max_optimizations=10):
        """SEO 自動最適化を実行"""
        self.log("\n" + "="*60)
        self.log("SEO 自動最適化エンジン 開始")
        self.log("="*60)
        
        # WordPress から記事を取得
        posts = self.fetch_wordpress_posts()
        
        if not posts:
            self.log("✗ 記事が見つかりませんでした")
            return
        
        # 検索順位データを取得（シミュレート）
        rank_data = self.simulate_search_rank_data(posts)
        
        # 順位が低下した記事を検出
        drop_posts = self.detect_rank_drop_posts(rank_data, threshold=5)
        
        if not drop_posts:
            self.log("✓ 順位が低下した記事はありませんでした")
            return
        
        # 最適化履歴を読み込み
        history = self.load_history()
        
        # 最大N件まで最適化
        optimized_count = 0
        for drop_post in drop_posts[:max_optimizations]:
            optimization_record = self.optimize_post(
                drop_post['post_id'],
                drop_post['post_title'],
                drop_post
            )
            
            if optimization_record:
                history.append(optimization_record)
                optimized_count += 1
        
        # 最適化履歴を保存
        self.save_history(history)
        
        self.log("\n" + "="*60)
        self.log(f"SEO 自動最適化エンジン 完了: {optimized_count}件の記事を最適化しました")
        self.log("="*60)


if __name__ == '__main__':
    optimizer = SEOAutoOptimizer()
    optimizer.run(max_optimizations=10)
