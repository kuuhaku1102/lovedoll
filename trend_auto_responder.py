#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
トレンド自動対応システム
最新トレンドを自動監視し、トレンドに応じた記事を自動生成
"""

import os
import json
import requests
from datetime import datetime
from openai import OpenAI
from generate_article_v3 import ArticleGenerator
from post_to_wordpress_v2 import WordPressPublisher

class TrendAutoResponder:
    def __init__(self):
        self.site_url = os.getenv('WP_SITE_URL')
        
        # OpenAI クライアント
        self.client = OpenAI()
        
        # 記事生成器
        self.article_generator = ArticleGenerator()
        
        # WordPress 投稿器
        self.wp_publisher = WordPressPublisher()
        
        # データファイルのパス
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.tracking_file = os.path.join(self.data_dir, 'trend_tracking.json')
        
        # ログファイル
        self.log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.log_file = os.path.join(self.log_dir, 'trend_detection.log')
    
    def log(self, message):
        """ログを記録"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def load_tracking(self):
        """トレンド追跡データを読み込み"""
        if os.path.exists(self.tracking_file):
            with open(self.tracking_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_tracking(self, tracking):
        """トレンド追跡データを保存"""
        with open(self.tracking_file, 'w', encoding='utf-8') as f:
            json.dump(tracking, f, ensure_ascii=False, indent=2)
    
    def detect_trending_keywords(self):
        """トレンドキーワードを検出（シミュレート）"""
        self.log("トレンドキーワードを検出中...")
        
        # 実際は Google Trends API を使用
        # ここではシミュレート
        trending_keywords = [
            {
                'keyword': 'ラブドール 新素材',
                'trend_score': 85,
                'search_volume': 1200,
                'growth_rate': 150
            },
            {
                'keyword': 'ラブドール AI搭載',
                'trend_score': 92,
                'search_volume': 800,
                'growth_rate': 200
            },
            {
                'keyword': 'ラブドール レンタル',
                'trend_score': 78,
                'search_volume': 500,
                'growth_rate': 120
            }
        ]
        
        # トレンドスコアでソート
        trending_keywords.sort(key=lambda x: x['trend_score'], reverse=True)
        
        self.log(f"✓ {len(trending_keywords)}件のトレンドキーワードを検出しました")
        
        for kw in trending_keywords:
            self.log(f"  - {kw['keyword']} (スコア: {kw['trend_score']})")
        
        return trending_keywords
    
    def is_keyword_already_covered(self, keyword, tracking):
        """キーワードが既に記事化されているか確認"""
        for record in tracking:
            if record['keyword'] == keyword and record['article_generated']:
                # 30日以内に記事化されている場合はスキップ
                detected_date = datetime.fromisoformat(record['detected_date'])
                days_passed = (datetime.now() - detected_date).days
                
                if days_passed < 30:
                    return True
        
        return False
    
    def generate_trend_article(self, keyword_info):
        """トレンドキーワードに応じた記事を生成"""
        keyword = keyword_info['keyword']
        
        self.log(f"\n[トレンド記事生成] キーワード: {keyword}")
        
        # 記事生成のプロンプトを作成
        prompt = f"""あなたはラブドール専門のコンテンツライターです。

【トレンドキーワード】
{keyword}

【記事の要件】
1. トレンドキーワードに焦点を当てた記事を生成
2. 最新の情報を提供
3. 読者の興味を引く内容
4. SEO を意識したタイトルと見出し
5. ラブドールを「美術品」「工芸品」として扱う
6. 性的な表現は一切含めない

【記事構成】
- タイトル（30〜40文字）
- 導入文（200文字程度）
- 本文（2000〜3000文字）
  - H2見出し3〜5個
  - 各セクションで具体的な情報を提供
- まとめ（200文字程度）

【出力形式】
Markdown 形式で出力してください。
"""
        
        response = self.client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        article_content = response.choices[0].message.content.strip()
        
        self.log(f"  ✓ トレンド記事を生成しました")
        
        return article_content
    
    def extract_title_from_article(self, article_content):
        """記事からタイトルを抽出"""
        lines = article_content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line.replace('# ', '').strip()
        
        return "トレンド記事"
    
    def publish_trend_article(self, keyword, article_content):
        """トレンド記事を WordPress に投稿"""
        self.log(f"  WordPress に投稿中...")
        
        title = self.extract_title_from_article(article_content)
        
        # 記事データを構築
        article_data = {
            'title': title,
            'content': article_content,
            'category': 'lovedoll-trends',  # トレンドカテゴリー
            'category_name': 'トレンド',
            'keywords': [keyword]
        }
        
        # WordPress に投稿
        try:
            post_id = self.wp_publisher.publish_article(article_data)
            
            if post_id:
                self.log(f"    ✓ 記事を投稿しました（ID: {post_id}）")
                return post_id
            else:
                self.log(f"    ✗ 記事の投稿に失敗しました")
                return None
        except Exception as e:
            self.log(f"    ✗ エラー: {str(e)}")
            return None
    
    def run(self, max_articles=1):
        """トレンド自動対応を実行"""
        self.log("\n" + "="*60)
        self.log("トレンド自動対応システム 開始")
        self.log("="*60)
        
        # トレンドキーワードを検出
        trending_keywords = self.detect_trending_keywords()
        
        if not trending_keywords:
            self.log("✓ トレンドキーワードが見つかりませんでした")
            return
        
        # トレンド追跡データを読み込み
        tracking = self.load_tracking()
        
        # 記事生成カウンター
        generated_count = 0
        
        for keyword_info in trending_keywords:
            keyword = keyword_info['keyword']
            
            # 既に記事化されているかチェック
            if self.is_keyword_already_covered(keyword, tracking):
                self.log(f"  ⚠ キーワード '{keyword}' は既に記事化されています（スキップ）")
                continue
            
            # トレンド記事を生成
            article_content = self.generate_trend_article(keyword_info)
            
            # WordPress に投稿
            post_id = self.publish_trend_article(keyword, article_content)
            
            if post_id:
                # トレンド追跡データに記録
                tracking.append({
                    'keyword': keyword,
                    'detected_date': datetime.now().isoformat(),
                    'trend_score': keyword_info['trend_score'],
                    'article_generated': True,
                    'post_id': post_id,
                    'category_added': False
                })
                
                generated_count += 1
                
                # 最大記事数に達したら終了
                if generated_count >= max_articles:
                    break
        
        # トレンド追跡データを保存
        self.save_tracking(tracking)
        
        self.log("\n" + "="*60)
        self.log(f"トレンド自動対応システム 完了: {generated_count}件のトレンド記事を生成しました")
        self.log("="*60)


if __name__ == '__main__':
    responder = TrendAutoResponder()
    responder.run(max_articles=1)
