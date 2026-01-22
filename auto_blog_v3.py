#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2026年SEO完全準拠 自動ブログ投稿システム v3.0
6ステップ完全実装版
"""

import sys
import os
from datetime import datetime

# スクリプトのディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(__file__))

# パス設定を調整
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from generate_article_v3 import SEOArticleGeneratorV3
from post_to_wordpress_v2 import WordPressPublisher


def main():
    print("="*60)
    print("2026年SEO完全準拠 自動ブログ投稿システム v3.0")
    print("6ステップ完全実装版")
    print("="*60)
    print(f"実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    print()
    
    try:
        # ステップ1-6: 記事生成（6ステップ）
        print("[記事生成] 6ステップ実行中...")
        print("-"*60)
        
        generator = SEOArticleGeneratorV3()
        article = generator.generate_article()
        
        if not article:
            print("\n✗ 記事生成に失敗しました")
            sys.exit(1)
        
        # 記事を保存
        json_file, md_file = generator.save_article(article)
        print(f"✓ 記事を保存: {json_file}")
        
        # WordPress投稿
        print("\n[WordPress投稿]")
        print("-"*60)
        
        publisher = WordPressPublisher()
        post = publisher.publish_article(article)
        
        if not post:
            print("\n✗ WordPress投稿に失敗しました")
            sys.exit(1)
        
        print("\n" + "="*60)
        print("✓ 自動ブログ投稿が完了しました")
        print("="*60)
        print(f"記事タイトル: {article['title']}")
        print(f"カテゴリ: {article['category_name']}")
        print(f"品質スコア: {article['quality_data']['score_total']}/60点")
        print(f"WordPress URL: {post['link']}")
        print()
        
    except Exception as e:
        print(f"\n✗ エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
