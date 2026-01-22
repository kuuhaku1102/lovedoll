#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTA（Call To Action）セクション自動生成システム
記事の最後に「おすすめ商品」セクションを自動生成
"""

import os
import json
import random


class CTAGenerator:
    def __init__(self, db_path='product_database.json'):
        self.db_path = os.path.join(os.path.dirname(__file__), db_path)
        self.db = self.load_database()
    
    def load_database(self):
        """商品データベースを読み込み"""
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"商品データベースが見つかりません: {self.db_path}")
    
    def select_products(self, category, max_products=3):
        """カテゴリーに応じた商品を選択"""
        products = self.db['products']
        
        # カテゴリーに一致する商品をフィルタリング
        matched_products = [
            p for p in products 
            if category in p['category']
        ]
        
        # 一致する商品がない場合はデフォルト商品を使用
        if not matched_products:
            print(f"⚠ カテゴリー '{category}' に一致する商品がありません。デフォルト商品を使用します。")
            matched_products = self.db['default_products']
        
        # 優先度でソート
        matched_products.sort(key=lambda x: x['priority'])
        
        # 最大N件を返す
        selected = matched_products[:max_products]
        
        print(f"✓ {len(selected)}件の商品を選択しました")
        for p in selected:
            print(f"  - {p['name']} ({p['shop_name']})")
        
        return selected
    
    def get_cta_template(self, category):
        """カテゴリーに応じたCTAテンプレートを取得"""
        templates = self.db['cta_templates']
        
        if category in templates:
            return templates[category]
        else:
            return templates['default']
    
    def generate_product_card_html(self, product):
        """商品カードのHTMLを生成"""
        features_html = '\n'.join([
            f'            <li>{feature}</li>'
            for feature in product['features']
        ])
        
        html = f'''
        <div class="product-card">
          <div class="product-image">
            <img src="{product['image_url']}" alt="{product['name']}" loading="lazy">
          </div>
          <div class="product-info">
            <h4 class="product-name">{product['name']}</h4>
            <p class="product-price">{product['price']}</p>
            <ul class="product-features">
{features_html}
            </ul>
            <div class="product-action">
              <a href="{product['affiliate_link']}" class="btn-primary" target="_blank" rel="noopener noreferrer">
                {product['shop_name']}で詳細を見る
              </a>
            </div>
          </div>
        </div>
'''
        return html
    
    def generate_cta_section(self, category, max_products=3):
        """CTAセクション全体のHTMLを生成"""
        # 商品を選択
        products = self.select_products(category, max_products)
        
        # CTAテンプレートを取得
        template = self.get_cta_template(category)
        
        # 商品カードを生成
        product_cards = '\n'.join([
            self.generate_product_card_html(p)
            for p in products
        ])
        
        # CTAセクション全体のHTML
        cta_html = f'''
<div class="cta-section">
  <div class="cta-header">
    <h3 class="cta-title">{template['title']}</h3>
    <p class="cta-description">{template['description']}</p>
  </div>
  <div class="product-grid">
{product_cards}
  </div>
  <div class="cta-footer">
    <p class="disclaimer">※ 価格は変動する場合があります。最新情報は各ショップでご確認ください。</p>
  </div>
</div>
'''
        
        return cta_html
    
    def add_cta_to_content(self, content, category, max_products=3):
        """記事コンテンツにCTAセクションを追加"""
        cta_html = self.generate_cta_section(category, max_products)
        
        # 記事の最後に追加
        # まとめセクションの後に挿入
        if '</article>' in content:
            # <article>タグがある場合は、その直前に挿入
            content = content.replace('</article>', f'{cta_html}\n</article>')
        else:
            # <article>タグがない場合は、最後に追加
            content += f'\n{cta_html}'
        
        print("✓ CTAセクションを記事に追加しました")
        
        return content


# テスト用
if __name__ == '__main__':
    generator = CTAGenerator()
    
    # テスト: 選び方カテゴリー
    print("\n=== テスト: 選び方カテゴリー ===")
    cta_html = generator.generate_cta_section('lovedoll-selection', max_products=3)
    print(cta_html)
    
    # テスト: メンテナンスカテゴリー
    print("\n=== テスト: メンテナンスカテゴリー ===")
    cta_html = generator.generate_cta_section('lovedoll-maintenance', max_products=2)
    print(cta_html)
