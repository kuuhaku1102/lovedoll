#!/usr/bin/env python3
"""
Keyword Manager for SEO Blog Auto-posting

This module manages keywords to ensure comprehensive coverage without duplication.
It tracks used keywords and selects the next available keyword for blog generation.

Features:
    - Keyword rotation without duplication
    - Persistent state management
    - Automatic reset after all keywords are used
    - Extensible keyword database
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Comprehensive keyword database for lovedoll topics
KEYWORD_DATABASE = [
    # ランキングページ関連（優先度高）
    "Sweet Doll おすすめ",
    "Sweet Doll レビュー",
    "Sweet Doll 評判",
    "Sweet Doll 購入ガイド",
    "Happiness Doll おすすめ",
    "Happiness Doll レビュー",
    "Happiness Doll 評判",
    "YourDoll おすすめ",
    "YourDoll レビュー",
    "YourDoll 評判",
    
    # 基本・選び方
    "ラブドール 選び方",
    "ラブドール おすすめ",
    "ラブドール 初心者",
    "ラブドール 購入ガイド",
    "ラブドール 比較",
    
    # メンテナンス・保管
    "ラブドール メンテナンス",
    "ラブドール 保管方法",
    "ラブドール 手入れ",
    "ラブドール 洗い方",
    "ラブドール 収納",
    
    # 材質・種類
    "ラブドール 価格",
    "ラブドール 種類",
    "ラブドール TPE シリコン 違い",
    "ラブドール TPE",
    "ラブドール シリコン",
    "ラブドール 材質",
    
    # サイズ・重量
    "ラブドール 軽量",
    "ラブドール 小型",
    "ラブドール サイズ",
    "ラブドール 身長",
    "ラブドール 重さ",
    
    # レビュー・評価
    "ラブドール レビュー",
    "ラブドール 口コミ",
    "ラブドール 評判",
    "ラブドール ランキング",
    
    # 購入・販売店
    "ラブドール 通販",
    "ラブドール 販売店",
    "ラブドール 正規品",
    "ラブドール 安全",
    "ラブドール 匿名配送",
    
    # カスタマイズ
    "ラブドール カスタマイズ",
    "ラブドール 顔",
    "ラブドール ウィッグ",
    "ラブドール 衣装",
    
    # 用途別
    "ラブドール 一人暮らし",
    "ラブドール 初めて",
    "ラブドール コスパ",
    "ラブドール 高級",
    "ラブドール リアル",
    
    # トラブル・Q&A
    "ラブドール 失敗",
    "ラブドール 注意点",
    "ラブドール よくある質問",
    "ラブドール トラブル",
    
    # その他
    "ラブドール 寿命",
    "ラブドール 修理",
    "ラブドール 処分",
    "ラブドール 保証",
    "ラブドール アフターサービス",
]


class KeywordManager:
    """Manage keywords for blog auto-posting."""
    
    def __init__(self, state_file: str = "keyword_state.json"):
        """
        Initialize the keyword manager.
        
        Args:
            state_file: Path to the state file for tracking used keywords
        """
        self.state_file = Path(state_file)
        self.keywords = KEYWORD_DATABASE.copy()
        self.state = self._load_state()
        
    def _load_state(self) -> Dict:
        """Load the keyword state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    logger.info(f"Loaded keyword state: {len(state.get('used_keywords', []))} keywords used")
                    return state
            except Exception as e:
                logger.warning(f"Failed to load state file: {e}")
        
        # Return default state
        return {
            "used_keywords": [],
            "current_cycle": 1,
            "last_updated": None,
            "total_posts": 0
        }
    
    def _save_state(self):
        """Save the keyword state to file."""
        try:
            self.state["last_updated"] = datetime.now().isoformat()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved keyword state: {len(self.state['used_keywords'])} keywords used")
        except Exception as e:
            logger.error(f"Failed to save state file: {e}")
    
    def get_next_keyword(self) -> Optional[str]:
        """
        Get the next available keyword that hasn't been used in the current cycle.
        
        Returns:
            The next keyword to use, or None if all keywords have been used
        """
        used_keywords = set(self.state.get("used_keywords", []))
        available_keywords = [kw for kw in self.keywords if kw not in used_keywords]
        
        if not available_keywords:
            logger.info("All keywords used in current cycle. Starting new cycle.")
            self._reset_cycle()
            available_keywords = self.keywords.copy()
        
        # Select the first available keyword
        next_keyword = available_keywords[0]
        logger.info(f"Selected keyword: {next_keyword} ({len(available_keywords)} remaining)")
        
        return next_keyword
    
    def mark_keyword_used(self, keyword: str):
        """
        Mark a keyword as used.
        
        Args:
            keyword: The keyword that was used
        """
        if keyword not in self.state["used_keywords"]:
            self.state["used_keywords"].append(keyword)
            self.state["total_posts"] += 1
            self._save_state()
            logger.info(f"Marked keyword as used: {keyword}")
    
    def _reset_cycle(self):
        """Reset the keyword cycle and start over."""
        self.state["used_keywords"] = []
        self.state["current_cycle"] += 1
        self._save_state()
        logger.info(f"Reset keyword cycle. Now on cycle {self.state['current_cycle']}")
    
    def get_stats(self) -> Dict:
        """
        Get statistics about keyword usage.
        
        Returns:
            Dictionary containing usage statistics
        """
        total_keywords = len(self.keywords)
        used_keywords = len(self.state.get("used_keywords", []))
        remaining_keywords = total_keywords - used_keywords
        
        return {
            "total_keywords": total_keywords,
            "used_keywords": used_keywords,
            "remaining_keywords": remaining_keywords,
            "current_cycle": self.state.get("current_cycle", 1),
            "total_posts": self.state.get("total_posts", 0),
            "last_updated": self.state.get("last_updated"),
            "progress_percentage": (used_keywords / total_keywords * 100) if total_keywords > 0 else 0
        }
    
    def list_remaining_keywords(self) -> List[str]:
        """
        Get a list of remaining keywords in the current cycle.
        
        Returns:
            List of unused keywords
        """
        used_keywords = set(self.state.get("used_keywords", []))
        return [kw for kw in self.keywords if kw not in used_keywords]
    
    def list_used_keywords(self) -> List[str]:
        """
        Get a list of used keywords in the current cycle.
        
        Returns:
            List of used keywords
        """
        return self.state.get("used_keywords", []).copy()


def main():
    """Main function for testing."""
    import argparse
    
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    parser = argparse.ArgumentParser(description="Keyword Manager for SEO Blog")
    parser.add_argument("--next", action="store_true", help="Get next keyword")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--list", action="store_true", help="List remaining keywords")
    parser.add_argument("--mark-used", type=str, help="Mark a keyword as used")
    parser.add_argument("--reset", action="store_true", help="Reset the cycle")
    
    args = parser.parse_args()
    
    manager = KeywordManager()
    
    if args.next:
        keyword = manager.get_next_keyword()
        print(f"Next keyword: {keyword}")
    
    elif args.stats:
        stats = manager.get_stats()
        print("Keyword Statistics:")
        print(f"  Total Keywords: {stats['total_keywords']}")
        print(f"  Used Keywords: {stats['used_keywords']}")
        print(f"  Remaining Keywords: {stats['remaining_keywords']}")
        print(f"  Current Cycle: {stats['current_cycle']}")
        print(f"  Total Posts: {stats['total_posts']}")
        print(f"  Progress: {stats['progress_percentage']:.1f}%")
        print(f"  Last Updated: {stats['last_updated']}")
    
    elif args.list:
        remaining = manager.list_remaining_keywords()
        print(f"Remaining Keywords ({len(remaining)}):")
        for i, kw in enumerate(remaining, 1):
            print(f"  {i}. {kw}")
    
    elif args.mark_used:
        manager.mark_keyword_used(args.mark_used)
        print(f"Marked as used: {args.mark_used}")
    
    elif args.reset:
        manager._reset_cycle()
        print("Cycle reset successfully")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
