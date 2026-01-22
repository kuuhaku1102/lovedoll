#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動コンテンツ提案システム
不足しているコンテンツを自動検出し、新規ページ・セクションを提案
"""

import os
import json
import requests
from datetime import datetime
from openai import OpenAI

class ContentAutoSuggester:
    def __init__(self):
        self.site_url = os.getenv('WP_SITE_URL')
        
        # OpenAI クライアント
        self.client = OpenAI()
        
        # データファイルのパス
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.suggestions_file = os.path.join(self.data_dir, 'content_suggestions.json')
        
        # ログファイル
        self.log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.log_file = os.path.join(self.log_dir, 'content_suggestion.log')
        
        # 競合サイトリスト
        self.competitor_sites = [
            'https://lovedoll-partner.com',
            'https://example-lovedoll-site.com',  # 実際の競合サイトに置き換え
        ]
    
    def log(self, message):
        """ログを記録"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def load_suggestions(self):
        """提案データを読み込み"""
        if os.path.exists(self.suggestions_file):
            with open(self.suggestions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_suggestions(self, suggestions):
        """提案データを保存"""
        with open(self.suggestions_file, 'w', encoding='utf-8') as f:
            json.dump(suggestions, f, ensure_ascii=False, indent=2)
    
    def fetch_own_site_structure(self):
        """自サイトのコンテンツ構造を取得"""
        self.log("自サイトのコンテンツ構造を取得中...")
        
        # カテゴリーを取得
        url = f"{self.site_url}/wp-json/wp/v2/categories"
        response = requests.get(url)
        
        if response.status_code != 200:
            self.log("✗ カテゴリーの取得に失敗しました")
            return {'categories': [], 'posts': []}
        
        categories = response.json()
        
        # 記事を取得
        url = f"{self.site_url}/wp-json/wp/v2/posts"
        params = {'per_page': 100, 'status': 'publish'}
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            self.log("✗ 記事の取得に失敗しました")
            return {'categories': categories, 'posts': []}
        
        posts = response.json()
        
        self.log(f"✓ カテゴリー: {len(categories)}件, 記事: {len(posts)}件")
        
        return {
            'categories': [c['name'] for c in categories],
            'posts': [p['title']['rendered'] for p in posts]
        }
    
    def analyze_competitor_site(self, site_url):
        """競合サイトを分析（シミュレート）"""
        self.log(f"競合サイトを分析中: {site_url}")
        
        # 実際は Web スクレイピングを使用
        # ここではシミュレート
        competitor_structure = {
            'categories': [
                'ラブドール 選び方',
                'ラブドール メンテナンス',
                'ラブドール レンタル',  # 自サイトにない
                'ラブドール 処分方法',  # 自サイトにない
                'ラブドール カスタマイズ'
            ],
            'popular_topics': [
                'ラブドール 処分方法',
                'ラブドール レンタル',
                'ラブドール 修理',
                'ラブドール 保険'
            ]
        }
        
        self.log(f"  ✓ カテゴリー: {len(competitor_structure['categories'])}件")
        
        return competitor_structure
    
    def detect_missing_content(self, own_structure, competitor_structures):
        """不足しているコンテンツを検出"""
        self.log("不足しているコンテンツを検出中...")
        
        own_categories = set(own_structure['categories'])
        own_posts = set(own_structure['posts'])
        
        missing_categories = set()
        missing_topics = set()
        
        # 各競合サイトと比較
        for comp_structure in competitor_structures:
            for category in comp_structure['categories']:
                if category not in own_categories:
                    missing_categories.add(category)
            
            for topic in comp_structure.get('popular_topics', []):
                # 記事タイトルに含まれていないトピック
                if not any(topic in post for post in own_posts):
                    missing_topics.add(topic)
        
        self.log(f"✓ 不足カテゴリー: {len(missing_categories)}件")
        self.log(f"✓ 不足トピック: {len(missing_topics)}件")
        
        return {
            'missing_categories': list(missing_categories),
            'missing_topics': list(missing_topics)
        }
    
    def prioritize_suggestions(self, missing_content):
        """提案の優先度を判定"""
        self.log("提案の優先度を判定中...")
        
        suggestions = []
        
        # カテゴリーの提案
        for category in missing_content['missing_categories']:
            # AI で優先度を判定
            priority = self.judge_priority(category, 'category')
            
            suggestions.append({
                'suggestion_date': datetime.now().isoformat(),
                'type': 'category',
                'title': category,
                'priority': priority,
                'reason': '競合サイトで取り扱いあり',
                'status': 'pending',
                'implementation_date': None
            })
        
        # トピックの提案
        for topic in missing_content['missing_topics']:
            # AI で優先度を判定
            priority = self.judge_priority(topic, 'article')
            
            suggestions.append({
                'suggestion_date': datetime.now().isoformat(),
                'type': 'article',
                'title': topic,
                'priority': priority,
                'reason': '競合サイトで人気トピック',
                'status': 'pending',
                'implementation_date': None
            })
        
        # 優先度でソート
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        suggestions.sort(key=lambda x: priority_order[x['priority']])
        
        self.log(f"✓ {len(suggestions)}件の提案を生成しました")
        
        return suggestions
    
    def judge_priority(self, content, content_type):
        """AI で優先度を判定"""
        prompt = f"""あなたはコンテンツ戦略の専門家です。

【コンテンツ】
{content}

【タイプ】
{content_type}

【判定基準】
- high: 検索ボリュームが高く、競合が多い。すぐに実装すべき。
- medium: 検索ボリュームは中程度。実装を検討すべき。
- low: 検索ボリュームが低い。優先度は低い。

【出力形式】
"high", "medium", "low" のいずれかのみを出力してください。説明は不要です。
"""
        
        response = self.client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        priority = response.choices[0].message.content.strip().lower()
        
        if priority not in ['high', 'medium', 'low']:
            priority = 'medium'
        
        return priority
    
    def generate_suggestion_report(self, suggestions):
        """提案レポートを生成"""
        self.log("提案レポートを生成中...")
        
        report = "# 自動コンテンツ提案レポート\n\n"
        report += f"生成日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n"
        
        report += "## 高優先度の提案\n\n"
        high_priority = [s for s in suggestions if s['priority'] == 'high']
        if high_priority:
            for s in high_priority:
                report += f"- **{s['title']}** ({s['type']})\n"
                report += f"  - 理由: {s['reason']}\n\n"
        else:
            report += "なし\n\n"
        
        report += "## 中優先度の提案\n\n"
        medium_priority = [s for s in suggestions if s['priority'] == 'medium']
        if medium_priority:
            for s in medium_priority:
                report += f"- **{s['title']}** ({s['type']})\n"
                report += f"  - 理由: {s['reason']}\n\n"
        else:
            report += "なし\n\n"
        
        report += "## 低優先度の提案\n\n"
        low_priority = [s for s in suggestions if s['priority'] == 'low']
        if low_priority:
            for s in low_priority:
                report += f"- **{s['title']}** ({s['type']})\n"
                report += f"  - 理由: {s['reason']}\n\n"
        else:
            report += "なし\n\n"
        
        # レポートを保存
        report_file = os.path.join(self.data_dir, 'content_suggestion_report.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.log(f"✓ 提案レポートを保存しました: {report_file}")
        
        return report
    
    def run(self, max_suggestions=5):
        """自動コンテンツ提案を実行"""
        self.log("\n" + "="*60)
        self.log("自動コンテンツ提案システム 開始")
        self.log("="*60)
        
        # 自サイトのコンテンツ構造を取得
        own_structure = self.fetch_own_site_structure()
        
        # 競合サイトを分析
        competitor_structures = []
        for site_url in self.competitor_sites:
            comp_structure = self.analyze_competitor_site(site_url)
            competitor_structures.append(comp_structure)
        
        # 不足しているコンテンツを検出
        missing_content = self.detect_missing_content(own_structure, competitor_structures)
        
        if not missing_content['missing_categories'] and not missing_content['missing_topics']:
            self.log("✓ 不足しているコンテンツはありませんでした")
            return
        
        # 提案を生成
        new_suggestions = self.prioritize_suggestions(missing_content)
        
        # 既存の提案を読み込み
        existing_suggestions = self.load_suggestions()
        
        # 新しい提案のみを追加（重複を避ける）
        existing_titles = {s['title'] for s in existing_suggestions}
        for suggestion in new_suggestions:
            if suggestion['title'] not in existing_titles:
                existing_suggestions.append(suggestion)
        
        # 提案を保存
        self.save_suggestions(existing_suggestions)
        
        # 提案レポートを生成
        report = self.generate_suggestion_report(new_suggestions[:max_suggestions])
        
        self.log("\n" + "="*60)
        self.log(f"自動コンテンツ提案システム 完了: {len(new_suggestions)}件の提案を生成しました")
        self.log("="*60)


if __name__ == '__main__':
    suggester = ContentAutoSuggester()
    suggester.run(max_suggestions=5)
