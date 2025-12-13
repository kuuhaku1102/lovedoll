#!/usr/bin/env python3
"""
Daily Auto-posting Script for SEO Blog

This script automatically generates and posts a blog article every day at 10:00 AM.
It uses the keyword manager to ensure comprehensive coverage without duplication.

Features:
    - Automatic keyword selection
    - Daily blog post generation
    - WordPress auto-posting
    - Error handling and logging
    - Email notifications (optional)

Usage:
    python auto_post_daily.py [--dry-run] [--force-keyword KEYWORD]
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from keyword_manager import KeywordManager
from generate_seo_blog import SEOBlogGenerator, WordPressPublisher

# Configure logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

log_file = LOG_DIR / f"auto_post_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configuration
WP_BASE_URL = os.getenv("WP_BASE_URL", "https://freya-era.com")
POST_STATUS = os.getenv("POST_STATUS", "publish")  # draft or publish
STATE_FILE = Path(__file__).parent / "keyword_state.json"


def send_notification(subject: str, message: str):
    """
    Send notification email (optional).
    
    Args:
        subject: Email subject
        message: Email message
    """
    # Placeholder for email notification
    # Implement this if you want email notifications
    logger.info(f"Notification: {subject}")
    logger.info(f"Message: {message}")


def main():
    """Main function for daily auto-posting."""
    parser = argparse.ArgumentParser(description="Daily Auto-posting for SEO Blog")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without actually posting to WordPress"
    )
    parser.add_argument(
        "--force-keyword",
        type=str,
        help="Force use of a specific keyword (for testing)"
    )
    parser.add_argument(
        "--status",
        type=str,
        choices=["draft", "publish"],
        default=POST_STATUS,
        help=f"Post status (default: {POST_STATUS})"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("Daily Auto-posting Script Started")
    logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"WordPress URL: {WP_BASE_URL}")
    logger.info(f"Post Status: {args.status}")
    logger.info(f"Dry Run: {args.dry_run}")
    logger.info("=" * 80)
    
    try:
        # Check for API key
        api_key = os.getenv("AI_API")
        if not api_key:
            error_msg = "AI_API environment variable is not set"
            logger.error(error_msg)
            send_notification("Auto-posting Failed", error_msg)
            return 1
        
        # Initialize keyword manager
        logger.info("Initializing keyword manager...")
        keyword_manager = KeywordManager(str(STATE_FILE))
        
        # Get statistics
        stats = keyword_manager.get_stats()
        logger.info(f"Keyword Statistics:")
        logger.info(f"  Total Keywords: {stats['total_keywords']}")
        logger.info(f"  Used Keywords: {stats['used_keywords']}")
        logger.info(f"  Remaining Keywords: {stats['remaining_keywords']}")
        logger.info(f"  Current Cycle: {stats['current_cycle']}")
        logger.info(f"  Progress: {stats['progress_percentage']:.1f}%")
        
        # Select keyword
        if args.force_keyword:
            keyword = args.force_keyword
            logger.info(f"Using forced keyword: {keyword}")
        else:
            keyword = keyword_manager.get_next_keyword()
            if not keyword:
                error_msg = "No available keywords"
                logger.error(error_msg)
                send_notification("Auto-posting Failed", error_msg)
                return 1
            logger.info(f"Selected keyword: {keyword}")
        
        # Generate blog post
        logger.info("Generating blog post with AI...")
        generator = SEOBlogGenerator(api_key)
        post_data = generator.generate_blog_post(keyword)
        
        logger.info("Blog post generated successfully:")
        logger.info(f"  Title: {post_data['title']}")
        logger.info(f"  Meta Description: {post_data['meta_description']}")
        logger.info(f"  Content Length: {len(post_data['content'])} characters")
        logger.info(f"  Tags: {', '.join(post_data['tags'])}")
        
        # Post to WordPress
        if args.dry_run:
            logger.info("DRY RUN: Skipping WordPress posting")
            logger.info("Post data:")
            logger.info(f"  Title: {post_data['title']}")
            logger.info(f"  Keyword: {keyword}")
            logger.info(f"  Status: {args.status}")
        else:
            logger.info("Publishing to WordPress...")
            publisher = WordPressPublisher(WP_BASE_URL)
            result = publisher.publish_post(post_data, args.status)
            
            logger.info("Post published successfully:")
            logger.info(f"  Post ID: {result.get('post_id', 'N/A')}")
            logger.info(f"  Permalink: {result.get('permalink', 'N/A')}")
            logger.info(f"  Status: {result.get('status', 'N/A')}")
            
            # Send success notification
            send_notification(
                "Auto-posting Successful",
                f"Blog post published successfully\n"
                f"Title: {post_data['title']}\n"
                f"Keyword: {keyword}\n"
                f"URL: {result.get('permalink', 'N/A')}"
            )
        
        # Mark keyword as used (even in dry run to prevent duplicates)
        if not args.force_keyword:
            keyword_manager.mark_keyword_used(keyword)
            logger.info(f"Marked keyword as used: {keyword}")
        
        logger.info("=" * 80)
        logger.info("Daily Auto-posting Script Completed Successfully")
        logger.info("=" * 80)
        
        return 0
        
    except Exception as e:
        error_msg = f"Auto-posting failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        send_notification("Auto-posting Failed", error_msg)
        return 1


if __name__ == "__main__":
    sys.exit(main())
