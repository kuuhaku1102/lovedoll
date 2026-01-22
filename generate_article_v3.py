#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026年SEO完全準拠 記事生成スクリプト v3.0
6ステップ完全実装版
"""

import os
import json
import datetime
from openai import OpenAI

class SEOArticleGeneratorV3:
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-4.1-mini"
        
        # カテゴリ設計を読み込み
        script_dir = os.path.dirname(os.path.abspath(__file__))
        seo_design_path = os.path.join(script_dir, 'seo_category_design.json')
        with open(seo_design_path, 'r', encoding='utf-8') as f:
            self.seo_design = json.load(f)
        
        # 記事履歴を読み込み
        self.history_file = os.path.join(script_dir, 'data', 'article_history.json')
        self.load_history()
        
        # スタイルガイド
        self.style_guide = self._load_style_guide()
    
    def _load_style_guide(self):
        """スタイルガイドを読み込み"""
        return """
# スタイルガイド
- 読者：初心者を含む一般読者
- トーン：丁寧・簡潔・実務的。煽らない
- 文章：結論→理由→具体例→手順→注意点→まとめ
- 1文は長くしすぎない。箇条書きを適切に使う
- 見出しは内容を言い切る（抽象語だけ禁止）
- 事実の断定を避ける：不確実は「一般に」「傾向として」で表現
- 数字・統計・法規・医療効果など"根拠が必要な断定"は禁止（引用なしでは書かない）
- 「当社」「実績」「体験談」「利用者の声」を捏造しない
- 競合名の誹謗中傷は禁止（比較は中立に）

# 禁止事項（絶対）
- 架空のデータ、架空の一次情報、架空の調査、架空の体験談
- 医療/健康/法律/投資などでの断定的助言（YMYL断定）
- 「必ず」「確実に」「100%」などの誇大表現
- コピペ調の冗長表現、同義反復
"""
    
    def load_history(self):
        """記事生成履歴を読み込み"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = {
                'articles': [],
                'current_category': 'medical-hair-removal',
                'category_progress': {}
            }
    
    def save_history(self):
        """記事生成履歴を保存"""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def get_current_category(self):
        """現在のカテゴリを取得"""
        current_slug = self.history.get('current_category', 'medical-hair-removal')
        
        for category in self.seo_design['categories']:
            if category['slug'] == current_slug:
                return category
        
        return self.seo_design['categories'][0]
    
    def switch_to_next_category_rotation(self):
        """次のカテゴリにローテーション"""
        current_slug = self.history['current_category']
        categories = self.seo_design['categories']
        
        for i, cat in enumerate(categories):
            if cat['slug'] == current_slug:
                next_index = (i + 1) % len(categories)
                self.history['current_category'] = categories[next_index]['slug']
                print(f"→ 次のカテゴリ: {categories[next_index]['name']}")
                return
    
    def get_next_article_role(self, category):
        """次に生成する記事の役割を取得（無制限ループ）"""
        category_slug = category['slug']
        
        if category_slug not in self.history['category_progress']:
            self.history['category_progress'][category_slug] = {
                'completed_roles': [],
                'article_count': 0
            }
        
        progress = self.history['category_progress'][category_slug]
        completed_roles = set(progress['completed_roles'])
        
        # まず未完了の役割を探す
        for role in category['article_roles']:
            role_key = f"{role['role']}_{role['priority']}"
            if role_key not in completed_roles:
                return role
        
        # すべての役割が完了している場合は、最初からループ
        # 優先順位が最も高い（priority=1）の役割を返す
        if category['article_roles']:
            return category['article_roles'][0]
        
        return None
    
    def step1_define_intent(self, category, role):
        """ステップ1: 検索意図・記事タイプ・ゴールを決定"""
        print("\n[ステップ1] 検索意図・記事タイプ・ゴールの決定")
        print("-" * 60)
        
        prompt = f"""あなたは日本語SEO編集長です。以下のスタイルガイドに必ず従ってください。

{self.style_guide}

# 入力
- メインKW：{category['name']} {role['role']}
- カテゴリ説明：{category['description']}
- 検索意図：{category['search_intent']}
- 記事の目的：{role['purpose']}
- 差別化ポイント：{role['differentiation']}
- 提供価値：ラブドール選びの判断材料提供
- CV（ゴール）：アフィリエイトリンクのクリック、詳細ページへの回遊

# タスク
1) 検索意図を以下で分類：情報収集 / 比較検討 / 行動（今すぐ）
2) 読者の状況を3段階（初心者・中級・決裁者など）で整理
3) 最適な記事タイプを選ぶ：
   - 用語解説
   - 手順HowTo
   - 比較ガイド
   - 選び方/失敗回避
   - FAQまとめ
4) この記事の「読了後に読者が取るべき行動」を1つに定義
5) 記事に入れるべき注意点（断定回避・リスク注意）を列挙

# 出力形式（JSON）
{{
  "intent": "",
  "reader_levels": ["", "", ""],
  "article_type": "",
  "primary_goal": "",
  "must_include_cautions": ["", "", ""]
}}
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        intent_data = json.loads(response.choices[0].message.content)
        print(f"✓ 検索意図: {intent_data['intent']}")
        print(f"✓ 記事タイプ: {intent_data['article_type']}")
        print(f"✓ ゴール: {intent_data['primary_goal']}")
        
        return intent_data
    
    def step2_design_structure(self, category, role, intent_data):
        """ステップ2: 見出し構造を設計"""
        print("\n[ステップ2] 見出し構造（H2/H3）の設計")
        print("-" * 60)
        
        prompt = f"""あなたは、美術品や工芸品を解説する専門雑誌の日本語編集長です。

【最重要指針】
- ラブドールを性的対象としてではなく、精巧な「美術品」「工芸品」として扱うこと。
- 性的・露骨な表現、性的利用を示唆する表現は一切使用しないこと。
- 品位を保ち、読者に有益な情報（技術、素材、メンテナンス方法など）を提供することに徹する。

{self.style_guide}

# 入力
- メインKW：{category['name']} {role['role']}
- 記事タイプ：{intent_data['article_type']}
- 検索意図：{intent_data['intent']}
- 読者レベル：{', '.join(intent_data['reader_levels'])}
- この記事のゴール：{intent_data['primary_goal']}

# タスク
- 上位を想定し、読者が知りたい論点を「漏れなく・ダブりなく」列挙
- 見出しは"検索意図の順番"で並べる（最初に結論・次に判断軸・最後に行動）
- H2は6〜10個、H3は必要なものだけ（過剰に増やさない）
- 「よくある失敗」「判断チェックリスト」「FAQ」を必ず含める
- この記事ならではの差別化要素を1つ入れる

# 出力（Markdown）
## タイトル案
1. （タイトル1）
2. （タイトル2）
3. （タイトル3）

## アウトライン
### H2: （見出し1）
- 要点1
- 要点2
- 要点3

### H2: （見出し2）
#### H3: （小見出し）
- 要点1
- 要点2
- 要点3

（以下同様）
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        
        structure = response.choices[0].message.content
        print("✓ 見出し構造を設計しました")
        
        return structure
    
    def step3_generate_sections(self, structure, intent_data):
        """ステップ3: セクション単位で本文生成"""
        print("\n[ステップ3] セクション単位での本文生成")
        print("-" * 60)
        
        # 見出しを抽出
        headings = []
        for line in structure.split('\n'):
            if line.startswith('### H2:') or line.startswith('#### H3:'):
                heading = line.replace('### H2:', '').replace('#### H3:', '').strip()
                if heading and not heading.startswith('（'):
                    headings.append(heading)
        
        sections = []
        for i, heading in enumerate(headings[:8]):  # 最大8セクション
            print(f"  生成中: {heading}")
            
            prompt = f"""あなたは、美術品や工芸品を解説する専門雑誌の日本語編集長です。

【最重要指針】
- ラブドールを性的対象としてではなく、精巧な「美術品」「工芸品」として扱うこと。
- 性的・露骨な表現、性的利用を示唆する表現は一切使用しないこと。
- 品位を保ち、読者に有益な情報（技術、素材、メンテナンス方法など）を提供することに徹する。

{self.style_guide}

# 入力
- 今回生成する見出し：{heading}
- 読者の状態：{intent_data['intent']} / {', '.join(intent_data['reader_levels'])}
- 禁止事項：捏造・断定・誇大表現禁止

# タスク
- 以下の構成で本文を作成：
  1) 結論（1〜2文）
  2) 理由（2〜4文）
  3) 具体例（1つ）
  4) 手順 or チェックポイント（箇条書き）
  5) 注意点（断定回避・条件）
- 文字数目安：300〜500文字
- 同じ言い回しを繰り返さない

# 出力（Markdown）
### {heading}
本文...
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            section_content = response.choices[0].message.content
            sections.append(section_content)
        
        print(f"✓ {len(sections)}セクションを生成しました")
        return sections
    
    def step4_integrate_article(self, structure, sections, category, role):
        """ステップ4: 全文の統合＋整形"""
        print("\n[ステップ4] 全文の統合＋整形")
        print("-" * 60)
        
        # タイトルを抽出
        title_lines = [line for line in structure.split('\n') if line.strip() and not line.startswith('#') and not line.startswith('-')]
        title = title_lines[0] if title_lines else role['title_example']
        
        sections_markdown = '\n\n'.join(sections)
        
        prompt = f"""あなたは、美術品や工芸品を解説する専門雑誌の日本語編集長です。

【最重要指針】
- ラブドールを性的対象としてではなく、精巧な「美術品」「工芸品」として扱うこと。
- 性的・露骨な表現、性的利用を示唆する表現は一切使用しないこと。
- 品位を保ち、読者に有益な情報（技術、素材、メンテナンス方法など）を提供することに徹する。

{self.style_guide}

# 入力
- タイトル：{title}
- 本文（各セクションのMarkdown）：
{sections_markdown}

# タスク
- 導入文を作る（読者の悩み→この記事で分かること→読み切りメリット）
- まとめ（結論・次の行動）を作る
- 見出しの重複・順序の破綻を修正
- 箇条書きの粒度を整える

# 出力（Markdown）
# {title}

（導入文）

（本文）

## まとめ
（まとめ）
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=4000
        )
        
        article = response.choices[0].message.content
        print("✓ 記事を統合しました")
        
        return article, title
    
    def step5_quality_gate(self, article, category, role):
        """ステップ5: 品質ゲート（自動審査）"""
        print("\n[ステップ5] 品質ゲート（自動審査）")
        print("-" * 60)
        
        prompt = f"""あなたはSEO品質監査官です。以下の観点で記事を採点し、修正指示を出してください。

{self.style_guide}

# 入力
- 記事全文：
{article}

- メインKW：{category['name']} {role['role']}
- 記事タイプ：{role['role']}
- 禁止事項：捏造・断定・誇大・YMYL助言

# 採点基準（各0〜10点）
1) 検索意図一致
2) 網羅性（不足論点がないか）
3) 具体性（抽象論の多さ）
4) 可読性（冗長・同義反復）
5) 安全性（断定・誇大・捏造リスク）
6) 独自性（テンプレ感の強さ）

# タスク
- 総合点を算出（60点満点）
- 50点未満なら「公開不可」。改善点を具体的に
- 重要修正は "差分指示" で出す
- 断定・誇大表現を見つけたら「置換案」を提示

# 出力（JSON）
{{
  "score_total": 0,
  "scores": {{"intent":0,"coverage":0,"specificity":0,"readability":0,"safety":0,"originality":0}},
  "publishable": true,
  "critical_issues": [],
  "section_fixes": []
}}
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        quality_data = json.loads(response.choices[0].message.content)
        print(f"✓ 総合点: {quality_data['score_total']}/60点")
        print(f"✓ 公開可否: {'可' if quality_data['publishable'] else '不可'}")
        
        if quality_data['critical_issues']:
            print(f"⚠ 重要な問題: {len(quality_data['critical_issues'])}件")
        
        return quality_data
    
    def step6_seo_optimization(self, article, category, role):
        """ステップ6: SEO最適化パッケージ"""
        print("\n[ステップ6] SEO最適化パッケージ")
        print("-" * 60)
        
        prompt = f"""あなたは日本語SEO編集長です。

# 入力
- 記事全文：
{article[:2000]}...

- メインKW：{category['name']} {role['role']}
- サブKW：{category['name']}, クリニック, 選び方, 料金, 効果

# タスク
1) title案 5個（28～32文字目安）
2) meta description案 3個（80～120文字目安）
3) FAQ 5個（記事内容と一致）
4) FAQ schema用のQ&A文（JSON-LD）

# 出力（JSON）
{{
  "titles": [],
  "descriptions": [],
  "faqs": [{{"q":"...","a":"..."}}],
  "faq_schema_jsonld": {{}}
}}
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        seo_data = json.loads(response.choices[0].message.content)
        print(f"✓ タイトル案: {len(seo_data.get('titles', []))}個")
        print(f"✓ FAQ: {len(seo_data.get('faqs', []))}個")
        
        return seo_data
    
    def generate_article(self):
        """6ステップで記事を生成"""
        print("="*60)
        print("2026年SEO完全準拠 記事生成システム v3.0")
        print("6ステップ完全実装版")
        print("="*60)
        
        # カテゴリーと役割を取得
        category = self.get_current_category()
        role = self.get_next_article_role(category)
        
        # 記事数制限を無効化：常に記事を生成する
        # roleがNoneの場合は、次のカテゴリーに移動
        if role is None:
            print(f"✓ カテゴリ「{category['name']}」の全役割が完了、次のカテゴリーへ")
            self.switch_to_next_category_rotation()
            self.save_history()
            category = self.get_current_category()
            role = self.get_next_article_role(category)
        
        print(f"\n現在のカテゴリ: {category['name']}")
        print(f"記事の役割: {role['role']}")
        print(f"優先順位: {role['priority']}")
        
        # ステップ1: 検索意図決定
        intent_data = self.step1_define_intent(category, role)
        
        # ステップ2: 見出し構造設計
        structure = self.step2_design_structure(category, role, intent_data)
        
        # ステップ3: セクション生成
        sections = self.step3_generate_sections(structure, intent_data)
        
        # ステップ4: 全文統合
        article, title = self.step4_integrate_article(structure, sections, category, role)
        
        # ステップ5: 品質ゲート
        quality_data = self.step5_quality_gate(article, category, role)
        
        if not quality_data['publishable']:
            print("\n✗ 品質基準を満たしていません。記事生成を中止します。")
            return None
        
        # ステップ6: SEO最適化
        seo_data = self.step6_seo_optimization(article, category, role)
        
        # 記事データを作成
        article_data = {
            'title': title,
            'content': article,
            'category': category['slug'],
            'category_name': category['name'],
            'role': role['role'],
            'priority': role['priority'],
            'intent_data': intent_data,
            'quality_data': quality_data,
            'seo_data': seo_data
        }
        
        # 履歴を更新
        self.history['articles'].append({
            'title': title,
            'category': category['slug'],
            'role': role['role'],
            'priority': role['priority'],
            'generated_at': datetime.datetime.now().isoformat(),
            'word_count': len(article),
            'quality_score': quality_data['score_total']
        })
        
        category_slug = category['slug']
        role_key = f"{role['role']}_{role['priority']}"
        self.history['category_progress'][category_slug]['completed_roles'].append(role_key)
        self.history['category_progress'][category_slug]['article_count'] += 1
        
        # 次のカテゴリーにローテーション
        self.switch_to_next_category_rotation()
        self.save_history()
        
        print(f"\n✓ 記事生成完了")
        print(f"  タイトル: {title}")
        print(f"  文字数: {len(article)}文字")
        print(f"  品質スコア: {quality_data['score_total']}/60点")
        print(f"  カテゴリ進捗: {self.history['category_progress'][category_slug]['article_count']}/{category['target_articles']}記事")
        
        return article_data
    
    def save_article(self, article_data):
        """記事をファイルに保存"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON形式で保存
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_filename = os.path.join(script_dir, 'data', 'articles', f"article_{timestamp}.json")
        os.makedirs(os.path.dirname(json_filename), exist_ok=True)
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(article_data, f, ensure_ascii=False, indent=2)
        
        # Markdown形式で保存
        md_filename = os.path.join(script_dir, 'data', 'articles', f"article_{timestamp}.md")
        md_content = f"""# {article_data['title']}

**カテゴリ**: {article_data['category_name']}
**役割**: {article_data['role']}
**優先順位**: {article_data['priority']}
**品質スコア**: {article_data['quality_data']['score_total']}/60点

---

{article_data['content']}

---

## SEO情報

### タイトル候補
{chr(10).join(f"{i+1}. {t}" for i, t in enumerate(article_data['seo_data'].get('titles', [])))}

### メタディスクリプション候補
{chr(10).join(f"{i+1}. {d}" for i, d in enumerate(article_data['seo_data'].get('descriptions', [])))}

### FAQ
{chr(10).join(f"Q: {faq['q']}{chr(10)}A: {faq['a']}{chr(10)}" for faq in article_data['seo_data'].get('faqs', []))}
"""
        
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"\n記事を保存しました: {json_filename}")
        print(f"Markdown: {md_filename}")
        
        return json_filename, md_filename


def main():
    generator = SEOArticleGeneratorV3()
    article = generator.generate_article()
    
    if article:
        generator.save_article(article)
        print("\n✓ 記事生成が完了しました")
    else:
        print("\n✗ 記事生成に失敗しました")


if __name__ == '__main__':
    main()
