#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内部リンク自動化システム
投稿済み記事のデータベースを管理し、自動的に内部リンクを挿入
"""

import os
import json
import re
from datetime import datetime


class InternalLinkManager:
    def __init__(self, db_path='../data/internal_links_db.json'):
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        self.db = self.load_database()
    
    def load_database(self):
        """データベースを読み込み"""
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                'articles': [],
                'last_updated': None
            }
    
    def save_database(self):
        """データベースを保存"""
        self.db['last_updated'] = datetime.now().isoformat()
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, ensure_ascii=False, indent=2)
    
    def add_article(self, article_data, post_url, post_id):
        """新しい記事をデータベースに追加"""
        # キーワードを抽出（タイトルと役割から）
        keywords = self.extract_keywords(article_data)
        
        article_entry = {
            'id': post_id,
            'title': article_data['title'],
            'url': post_url,
            'category': article_data['category'],
            'category_name': article_data['category_name'],
            'role': article_data['role'],
            'keywords': keywords,
            'created_at': datetime.now().isoformat()
        }
        
        self.db['articles'].append(article_entry)
        self.save_database()
        
        print(f"✓ 内部リンクDBに追加: {article_data['title']}")
        print(f"  キーワード: {', '.join(keywords[:5])}")
    
    def extract_keywords(self, article_data):
        """記事からキーワードを抽出"""
        keywords = []
        
        # カテゴリー名をキーワードに追加
        keywords.append(article_data['category_name'])
        
        # タイトルから重要なキーワードを抽出
        title = article_data['title']
        
        # 「とは」「方法」「効果」などの一般的なパターンを除外
        stop_words = ['とは', 'とは？', '方法', '効果', '料金', '相場', '解説', '徹底', '完全', 
                      'ガイド', '初心者', '向け', 'まとめ', '比較', 'おすすめ', '人気']
        
        # タイトルを分割してキーワード候補を抽出
        # 例: 「医療脱毛の料金相場を徹底解説」→「医療脱毛」
        for stop in stop_words:
            title = title.replace(stop, '|')
        
        parts = [p.strip() for p in title.split('|') if p.strip()]
        keywords.extend(parts)
        
        # 役割から追加キーワードを抽出
        role = article_data['role']
        if '部位別' in role:
            # 例: 「部位別解説（VIO）」→「VIO脱毛」
            match = re.search(r'（(.+?)）', role)
            if match:
                part = match.group(1)
                keywords.append(f"{part}{article_data['category_name']}")
                keywords.append(part)
        
        # 重複を削除し、長さでソート（長いキーワードを優先）
        keywords = list(set(keywords))
        keywords.sort(key=len, reverse=True)
        
        return keywords
    
    def find_related_articles(self, article_data, max_links=5):
        """関連記事を検索"""
        if not self.db['articles']:
            return []
        
        current_category = article_data['category']
        content = article_data['content']
        
        # スコアリング
        scored_articles = []
        
        for article in self.db['articles']:
            score = 0
            matched_keywords = []
            
            # 同じカテゴリーはスコア+10
            if article['category'] == current_category:
                score += 10
            
            # キーワードマッチング
            for keyword in article['keywords']:
                if len(keyword) >= 3 and keyword in content:
                    score += len(keyword)  # 長いキーワードほど高スコア
                    matched_keywords.append(keyword)
            
            if score > 0:
                scored_articles.append({
                    'article': article,
                    'score': score,
                    'matched_keywords': matched_keywords
                })
        
        # スコア順にソート
        scored_articles.sort(key=lambda x: x['score'], reverse=True)
        
        # 上位N件を返す
        return scored_articles[:max_links]
    
    def insert_internal_links(self, content, article_data, max_links=5):
        """コンテンツに内部リンクを自動挿入"""
        related = self.find_related_articles(article_data, max_links)
        
        if not related:
            print("⚠ 関連記事が見つかりませんでした")
            return content
        
        print(f"\n✓ 関連記事を{len(related)}件発見")
        
        # HTMLに変換済みのコンテンツに対してリンクを挿入
        modified_content = content
        inserted_count = 0
        
        for item in related:
            article = item['article']
            keywords = item['matched_keywords']
            
            # 最も長いキーワードを使用（より具体的）
            if not keywords:
                continue
            
            keyword = keywords[0]
            
            # すでにリンクが存在する場合はスキップ
            if article['url'] in modified_content:
                continue
            
            # キーワードの最初の出現箇所にリンクを挿入
            # ただし、すでにリンクになっている箇所は避ける
            # 正規表現をシンプルにして、リンク内を避ける
            pattern = re.compile(r'\b(' + re.escape(keyword) + r')\b', re.IGNORECASE)
            
            # 最初の1箇所だけリンクに変換（すでに<a>タグ内にある場合はスキップ）
            matches = list(pattern.finditer(modified_content))
            for match in matches:
                # マッチ位置が<a>タグ内かチェック
                start_pos = match.start()
                # その位置より前に最後の<a>と</a>を探す
                before_text = modified_content[:start_pos]
                last_a_open = before_text.rfind('<a ')
                last_a_close = before_text.rfind('</a>')
                
                # <a>の後に</a>がない場合はリンク内なのでスキップ
                if last_a_open > last_a_close:
                    continue
                
                # リンク挿入
                link_html = f'<a href="{article["url"]}" class="internal-link">{match.group(1)}</a>'
                modified_content = modified_content[:match.start()] + link_html + modified_content[match.end():]
                inserted_count += 1
                print(f"  → リンク挿入: 「{keyword}」→「{article['title']}」")
                break  # 最初の1箇所だけ
        
        if inserted_count > 0:
            print(f"✓ {inserted_count}個の内部リンクを挿入しました")
        else:
            print("⚠ 内部リンクを挿入できませんでした")
        
        return modified_content
    
    def get_stats(self):
        """データベースの統計情報を取得"""
        total = len(self.db['articles'])
        by_category = {}
        
        for article in self.db['articles']:
            cat = article['category_name']
            by_category[cat] = by_category.get(cat, 0) + 1
        
        return {
            'total_articles': total,
            'by_category': by_category,
            'last_updated': self.db.get('last_updated')
        }
