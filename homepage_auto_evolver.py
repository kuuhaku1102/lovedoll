#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TOP ページ自動進化システム
TOP ページを自動的に更新し、常に最新の情報を表示
"""

import os
import json
import requests
import shutil
from datetime import datetime
from openai import OpenAI

class HomepageAutoEvolver:
    def __init__(self):
        self.site_url = os.getenv('WP_SITE_URL')
        
        # OpenAI クライアント
        self.client = OpenAI()
        
        # データファイルのパス
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.evolution_file = os.path.join(self.data_dir, 'homepage_evolution.json')
        
        # バックアップディレクトリ
        self.backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # ログファイル
        self.log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.log_file = os.path.join(self.log_dir, 'homepage_evolution.log')
        
        # front-page.php のパス
        self.homepage_file = os.path.join(os.path.dirname(__file__), 'front-page.php')
    
    def log(self, message):
        """ログを記録"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def load_evolution_history(self):
        """進化履歴を読み込み"""
        if os.path.exists(self.evolution_file):
            with open(self.evolution_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_evolution_history(self, history):
        """進化履歴を保存"""
        with open(self.evolution_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def backup_homepage(self):
        """front-page.php をバックアップ"""
        if not os.path.exists(self.homepage_file):
            self.log("⚠ front-page.php が見つかりません")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(self.backup_dir, f'front-page-backup-{timestamp}.php')
        
        shutil.copy2(self.homepage_file, backup_file)
        
        self.log(f"✓ front-page.php をバックアップしました: {backup_file}")
        
        return backup_file
    
    def fetch_popular_posts(self, limit=5):
        """人気記事を取得（シミュレート）"""
        self.log("人気記事を取得中...")
        
        # 実際は Google Analytics API を使用
        # ここではシミュレート
        url = f"{self.site_url}/wp-json/wp/v2/posts"
        params = {'per_page': limit, 'status': 'publish'}
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            self.log("✗ 人気記事の取得に失敗しました")
            return []
        
        posts = response.json()
        
        popular_posts = []
        for post in posts:
            popular_posts.append({
                'id': post['id'],
                'title': post['title']['rendered'],
                'link': post['link']
            })
        
        self.log(f"✓ {len(popular_posts)}件の人気記事を取得しました")
        
        return popular_posts
    
    def fetch_trend_posts(self, limit=3):
        """トレンド記事を取得"""
        self.log("トレンド記事を取得中...")
        
        # トレンド追跡データから最新のトレンド記事を取得
        trend_tracking_file = os.path.join(self.data_dir, 'trend_tracking.json')
        
        if not os.path.exists(trend_tracking_file):
            self.log("⚠ トレンド追跡データが見つかりません")
            return []
        
        with open(trend_tracking_file, 'r', encoding='utf-8') as f:
            tracking = json.load(f)
        
        # 記事が生成されているトレンドのみ
        trend_posts = []
        for record in tracking:
            if record['article_generated'] and 'post_id' in record:
                trend_posts.append({
                    'id': record['post_id'],
                    'keyword': record['keyword'],
                    'trend_score': record['trend_score']
                })
        
        # トレンドスコアでソート
        trend_posts.sort(key=lambda x: x['trend_score'], reverse=True)
        
        # 最大N件
        trend_posts = trend_posts[:limit]
        
        self.log(f"✓ {len(trend_posts)}件のトレンド記事を取得しました")
        
        return trend_posts
    
    def generate_popular_posts_section(self, popular_posts):
        """人気記事セクションの HTML を生成"""
        self.log("人気記事セクションを生成中...")
        
        posts_html = ""
        for post in popular_posts:
            posts_html += f'''
        <div class="popular-post-item">
          <h4><a href="{post['link']}">{post['title']}</a></h4>
        </div>
'''
        
        section_html = f'''
<section class="popular-posts-section">
  <div class="container">
    <h2 class="section-title">📊 人気記事</h2>
    <div class="popular-posts-grid">
{posts_html}
    </div>
  </div>
</section>
'''
        
        self.log("✓ 人気記事セクションを生成しました")
        
        return section_html
    
    def generate_trend_posts_section(self, trend_posts):
        """トレンド記事セクションの HTML を生成"""
        if not trend_posts:
            return ""
        
        self.log("トレンド記事セクションを生成中...")
        
        posts_html = ""
        for post in trend_posts:
            # WordPress から記事情報を取得
            url = f"{self.site_url}/wp-json/wp/v2/posts/{post['id']}"
            response = requests.get(url)
            
            if response.status_code == 200:
                post_data = response.json()
                posts_html += f'''
        <div class="trend-post-item">
          <span class="trend-badge">🔥 トレンド</span>
          <h4><a href="{post_data['link']}">{post_data['title']['rendered']}</a></h4>
        </div>
'''
        
        section_html = f'''
<section class="trend-posts-section">
  <div class="container">
    <h2 class="section-title">🔥 トレンド記事</h2>
    <div class="trend-posts-grid">
{posts_html}
    </div>
  </div>
</section>
'''
        
        self.log("✓ トレンド記事セクションを生成しました")
        
        return section_html
    
    def update_homepage(self, popular_section, trend_section):
        """front-page.php を更新"""
        self.log("front-page.php を更新中...")
        
        if not os.path.exists(self.homepage_file):
            self.log("✗ front-page.php が見つかりません")
            return False
        
        # 現在の front-page.php を読み込み
        with open(self.homepage_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 既存の人気記事セクションを削除
        import re
        content = re.sub(
            r'<section class="popular-posts-section">.*?</section>',
            '',
            content,
            flags=re.DOTALL
        )
        
        # 既存のトレンド記事セクションを削除
        content = re.sub(
            r'<section class="trend-posts-section">.*?</section>',
            '',
            content,
            flags=re.DOTALL
        )
        
        # 新しいセクションを挿入（<?php get_footer(); ?> の直前）
        new_sections = f"{trend_section}\n{popular_section}\n"
        
        content = content.replace(
            '<?php get_footer(); ?>',
            f'{new_sections}\n<?php get_footer(); ?>'
        )
        
        # front-page.php に書き込み
        with open(self.homepage_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.log("✓ front-page.php を更新しました")
        
        return True
    
    def run(self):
        """TOP ページ自動進化を実行"""
        self.log("\n" + "="*60)
        self.log("TOP ページ自動進化システム 開始")
        self.log("="*60)
        
        # front-page.php をバックアップ
        backup_file = self.backup_homepage()
        
        if not backup_file:
            self.log("✗ バックアップに失敗しました")
            return
        
        # 人気記事を取得
        popular_posts = self.fetch_popular_posts(limit=5)
        
        # トレンド記事を取得
        trend_posts = self.fetch_trend_posts(limit=3)
        
        # 人気記事セクションを生成
        popular_section = self.generate_popular_posts_section(popular_posts)
        
        # トレンド記事セクションを生成
        trend_section = self.generate_trend_posts_section(trend_posts)
        
        # front-page.php を更新
        success = self.update_homepage(popular_section, trend_section)
        
        if success:
            # 進化履歴を記録
            history = self.load_evolution_history()
            
            changes = []
            
            if popular_posts:
                changes.append({
                    'type': 'popular_posts',
                    'action': 'updated',
                    'posts': [p['id'] for p in popular_posts]
                })
            
            if trend_posts:
                changes.append({
                    'type': 'trend_posts',
                    'action': 'updated',
                    'posts': [p['id'] for p in trend_posts]
                })
            
            history.append({
                'update_date': datetime.now().isoformat(),
                'changes': changes,
                'backup_file': os.path.basename(backup_file)
            })
            
            self.save_evolution_history(history)
        
        self.log("\n" + "="*60)
        self.log("TOP ページ自動進化システム 完了")
        self.log("="*60)


if __name__ == '__main__':
    evolver = HomepageAutoEvolver()
    evolver.run()
