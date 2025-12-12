#!/usr/bin/env python3
"""
AI-powered SEO Blog Generator for Lovedoll Keywords

This script generates SEO-optimized blog posts about lovedoll-related topics
using the AI_API environment variable and posts them to WordPress.

Requirements:
    pip install requests openai

Usage:
    export AI_API="your-api-key-here"
    python generate_seo_blog.py --keyword "ラブドール 選び方" --wp-base "https://freya-era.com"

Environment Variables:
    AI_API: OpenAI-compatible API key (required)

Features:
    - SEO-optimized content generation
    - Keyword-focused article structure
    - Meta description generation
    - Internal linking suggestions
    - Automatic WordPress posting
"""

import argparse
import json
import logging
import os
import sys
from typing import Dict, List, Optional
from datetime import datetime

import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

WP_BASE_DEFAULT = "https://freya-era.com"
REQUEST_TIMEOUT = 30

# Lovedoll-related keyword templates
KEYWORD_TEMPLATES = [
    "ラブドール 選び方",
    "ラブドール おすすめ",
    "ラブドール 初心者",
    "ラブドール メンテナンス",
    "ラブドール 保管方法",
    "ラブドール 価格",
    "ラブドール 種類",
    "ラブドール TPE シリコン 違い",
    "ラブドール 購入ガイド",
    "ラブドール レビュー",
]


class SEOBlogGenerator:
    """Generate SEO-optimized blog posts using AI."""
    
    def __init__(self, api_key: str):
        """Initialize the generator with API key."""
        if not api_key:
            raise ValueError("AI_API environment variable is not set")
        
        self.api_key = api_key
        self.api_base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = "gpt-4.1-mini"  # Using the available model
        
    def generate_blog_post(self, keyword: str) -> Dict[str, str]:
        """
        Generate a complete SEO-optimized blog post.
        
        Args:
            keyword: Target keyword for the blog post
            
        Returns:
            Dictionary containing title, content, meta_description, and tags
        """
        logger.info(f"Generating blog post for keyword: {keyword}")
        
        prompt = self._create_seo_prompt(keyword)
        
        try:
            response = self._call_ai_api(prompt)
            result = self._parse_response(response, keyword)
            result["keyword"] = keyword  # Add keyword to result
            return result
        except Exception as e:
            logger.error(f"Failed to generate blog post: {e}")
            raise
    
    def _create_seo_prompt(self, keyword: str) -> str:
        """Create an SEO-optimized prompt for the AI."""
        return f"""あなたはSEOに精通したプロのコンテンツライターです。以下のキーワードについて、検索エンジンで上位表示されるような高品質なブログ記事を作成してください。

ターゲットキーワード: {keyword}

記事の要件:
1. タイトル: キーワードを含む魅力的なタイトル（30-40文字）
2. メタディスクリプション: 検索結果に表示される説明文（120-160文字）
3. 本文: 2000-3000文字の詳細な記事
   - 見出し（H2, H3）を適切に使用
   - キーワードを自然に含める（キーワード密度: 1-2%）
   - 読者に価値を提供する実用的な情報
   - 専門性、権威性、信頼性（E-E-A-T）を意識
4. タグ: 関連する5-7個のタグ

記事構成:
- 導入（問題提起・共感）
- 本論（具体的な解決策・ノウハウ）
- まとめ（行動喚起）

出力形式（JSON）:
{{
  "title": "記事タイトル",
  "meta_description": "メタディスクリプション",
  "content": "本文（HTML形式、見出しタグ付き）",
  "tags": ["タグ1", "タグ2", "タグ3"]
}}

必ずJSON形式で出力してください。"""
    
    def _call_ai_api(self, prompt: str) -> str:
        """Call the AI API to generate content."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "あなたはSEOに精通したプロのコンテンツライターです。高品質で読者に価値を提供する記事を作成します。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        logger.info(f"Calling AI API: {self.api_base}/chat/completions")
        
        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        return content
    
    def _parse_response(self, response: str, keyword: str) -> Dict[str, str]:
        """Parse the AI response and extract structured data."""
        try:
            # Try to extract JSON from the response
            # Sometimes the AI wraps JSON in markdown code blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()
            
            data = json.loads(json_str)
            
            return {
                "title": data.get("title", f"{keyword}について"),
                "content": data.get("content", ""),
                "meta_description": data.get("meta_description", ""),
                "tags": data.get("tags", [keyword])
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response: {response}")
            
            # Fallback: return basic structure
            return {
                "title": f"{keyword}について",
                "content": response,
                "meta_description": f"{keyword}に関する詳しい情報をご紹介します。",
                "tags": [keyword]
            }


class WordPressPublisher:
    """Publish blog posts to WordPress."""
    
    def __init__(self, wp_base: str):
        """Initialize the publisher with WordPress base URL."""
        self.wp_base = wp_base.rstrip("/")
        self.api_endpoint = f"{self.wp_base}/wp-json/lovedoll/v1/create-blog-post"
        
    def publish_post(self, post_data: Dict[str, str], status: str = "draft") -> Dict:
        """
        Publish a blog post to WordPress.
        
        Args:
            post_data: Dictionary containing title, content, meta_description, tags
            status: Post status (draft, publish)
            
        Returns:
            WordPress API response
        """
        logger.info(f"Publishing post to WordPress: {post_data['title']}")
        
        # Prepare WordPress post data
        wp_post = {
            "title": post_data["title"],
            "content": post_data["content"],
            "status": status,
            "excerpt": post_data.get("meta_description", ""),
            "meta_description": post_data.get("meta_description", ""),
            "tags": post_data.get("tags", []),
            "keyword": post_data.get("keyword", "")
        }
        
        try:
            response = requests.post(
                self.api_endpoint,
                json=wp_post,
                timeout=REQUEST_TIMEOUT
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Post published successfully: {result.get('link', 'N/A')}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to publish post: {e}")
            raise
    
    def _get_or_create_tags_unused(self, tag_names: List[str]) -> List[int]:
        """Get or create WordPress tags and return their IDs."""
        tag_ids = []
        tags_endpoint = f"{self.wp_base}/wp-json/wp/v2/tags"
        
        for tag_name in tag_names:
            try:
                # Search for existing tag
                response = requests.get(
                    tags_endpoint,
                    params={"search": tag_name},
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    tags = response.json()
                    if tags:
                        tag_ids.append(tags[0]["id"])
                        continue
                
                # Create new tag if not found
                response = requests.post(
                    tags_endpoint,
                    json={"name": tag_name},
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 201:
                    tag_ids.append(response.json()["id"])
                    
            except Exception as e:
                logger.warning(f"Failed to process tag '{tag_name}': {e}")
                continue
        
        return tag_ids


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Generate SEO-optimized blog posts for lovedoll keywords"
    )
    parser.add_argument(
        "--keyword",
        type=str,
        help="Target keyword for the blog post"
    )
    parser.add_argument(
        "--wp-base",
        type=str,
        default=WP_BASE_DEFAULT,
        help=f"WordPress base URL (default: {WP_BASE_DEFAULT})"
    )
    parser.add_argument(
        "--status",
        type=str,
        default="draft",
        choices=["draft", "publish"],
        help="Post status (default: draft)"
    )
    parser.add_argument(
        "--list-keywords",
        action="store_true",
        help="List available keyword templates"
    )
    
    args = parser.parse_args()
    
    # List keywords if requested
    if args.list_keywords:
        print("Available keyword templates:")
        for i, kw in enumerate(KEYWORD_TEMPLATES, 1):
            print(f"  {i}. {kw}")
        return 0
    
    # Check for API key
    api_key = os.getenv("AI_API")
    if not api_key:
        logger.error("AI_API environment variable is not set")
        logger.info("Please set it with: export AI_API='your-api-key-here'")
        return 1
    
    # Use provided keyword or select from templates
    keyword = args.keyword
    if not keyword:
        logger.info("No keyword provided, using default: ラブドール 選び方")
        keyword = "ラブドール 選び方"
    
    try:
        # Generate blog post
        generator = SEOBlogGenerator(api_key)
        post_data = generator.generate_blog_post(keyword)
        
        logger.info("=" * 60)
        logger.info(f"Title: {post_data['title']}")
        logger.info(f"Meta Description: {post_data['meta_description']}")
        logger.info(f"Tags: {', '.join(post_data['tags'])}")
        logger.info(f"Content Length: {len(post_data['content'])} characters")
        logger.info("=" * 60)
        
        # Publish to WordPress
        publisher = WordPressPublisher(args.wp_base)
        result = publisher.publish_post(post_data, args.status)
        
        logger.info("✓ Blog post generated and published successfully!")
        logger.info(f"Post ID: {result.get('id', 'N/A')}")
        logger.info(f"Post URL: {result.get('link', 'N/A')}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to generate or publish blog post: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
