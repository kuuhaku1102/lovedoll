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
    - Special keyword frequency control (ranking-related keywords)
"""

import json
import logging
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Comprehensive keyword database for lovedoll topics
# ランキングページ関連キーワード（1-2週間に1回程度）
RANKING_KEYWORDS = [
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
]

# 通常のSEOキーワード（毎日使用）
REGULAR_KEYWORDS = [
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

# ランキングキーワードの使用頻度（日数）
RANKING_KEYWORD_INTERVAL = 10  # 10日に1回


class KeywordManager:
    """Manage keywords for blog auto-posting."""
    
    def __init__(self, state_file: str = "keyword_state.json"):
        """
        Initialize the keyword manager.
        
        Args:
            state_file: Path to the state file for tracking used keywords
        """
        self.state_file = Path(state_file)
        self.regular_keywords = REGULAR_KEYWORDS.copy()
        self.ranking_keywords = RANKING_KEYWORDS.copy()
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
            "used_regular_keywords": [],
            "used_ranking_keywords": [],
            "last_ranking_keyword_date": None,
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
    
    def _should_use_ranking_keyword(self) -> bool:
        """
        Determine if a ranking keyword should be used based on the interval.
        
        Returns:
            True if a ranking keyword should be used, False otherwise
        """
        last_date = self.state.get("last_ranking_keyword_date")
        
        if not last_date:
            # Never used a ranking keyword before
            return True
        
        try:
            last_datetime = datetime.fromisoformat(last_date)
            days_since_last = (datetime.now() - last_datetime).days
            
            if days_since_last >= RANKING_KEYWORD_INTERVAL:
                logger.info(f"Using ranking keyword (last used {days_since_last} days ago)")
                return True
            else:
                logger.info(f"Skipping ranking keyword (last used {days_since_last} days ago, need {RANKING_KEYWORD_INTERVAL})")
                return False
        except Exception as e:
            logger.warning(f"Failed to parse last ranking keyword date: {e}")
            return True
    
    def get_next_keyword(self) -> Optional[str]:
        """
        Get the next available keyword that hasn't been used in the current cycle.
        
        Returns:
            The next keyword to use, or None if all keywords have been used
        """
        # Check if we should use a ranking keyword
        use_ranking = self._should_use_ranking_keyword()
        
        if use_ranking:
            # Get available ranking keywords
            used_ranking = set(self.state.get("used_ranking_keywords", []))
            available_ranking = [kw for kw in self.ranking_keywords if kw not in used_ranking]
            
            if available_ranking:
                # Randomly select from available ranking keywords
                next_keyword = random.choice(available_ranking)
                logger.info(f"Selected ranking keyword: {next_keyword} ({len(available_ranking)} ranking keywords remaining)")
                return next_keyword
            else:
                # All ranking keywords used, reset
                logger.info("All ranking keywords used. Resetting ranking keywords.")
                self.state["used_ranking_keywords"] = []
                next_keyword = random.choice(self.ranking_keywords)
                logger.info(f"Selected ranking keyword (after reset): {next_keyword}")
                return next_keyword
        
        # Use regular keyword
        used_regular = set(self.state.get("used_regular_keywords", []))
        available_regular = [kw for kw in self.regular_keywords if kw not in used_regular]
        
        if not available_regular:
            logger.info("All regular keywords used in current cycle. Starting new cycle.")
            self._reset_regular_cycle()
            available_regular = self.regular_keywords.copy()
        
        # Randomly select from available regular keywords
        next_keyword = random.choice(available_regular)
        logger.info(f"Selected regular keyword: {next_keyword} ({len(available_regular)} regular keywords remaining)")
        
        return next_keyword
    
    def mark_keyword_used(self, keyword: str):
        """
        Mark a keyword as used.
        
        Args:
            keyword: The keyword that was used
        """
        # Add to general used keywords
        if keyword not in self.state["used_keywords"]:
            self.state["used_keywords"].append(keyword)
            self.state["total_posts"] += 1
        
        # Add to specific category
        if keyword in self.ranking_keywords:
            if keyword not in self.state.get("used_ranking_keywords", []):
                if "used_ranking_keywords" not in self.state:
                    self.state["used_ranking_keywords"] = []
                self.state["used_ranking_keywords"].append(keyword)
                self.state["last_ranking_keyword_date"] = datetime.now().isoformat()
                logger.info(f"Marked ranking keyword as used: {keyword}")
        else:
            if keyword not in self.state.get("used_regular_keywords", []):
                if "used_regular_keywords" not in self.state:
                    self.state["used_regular_keywords"] = []
                self.state["used_regular_keywords"].append(keyword)
                logger.info(f"Marked regular keyword as used: {keyword}")
        
        self._save_state()
    
    def _reset_regular_cycle(self):
        """Reset the regular keyword cycle and start over."""
        self.state["used_regular_keywords"] = []
        self.state["current_cycle"] += 1
        self._save_state()
        logger.info(f"Reset regular keyword cycle. Now on cycle {self.state['current_cycle']}")
    
    def get_stats(self) -> Dict:
        """
        Get statistics about keyword usage.
        
        Returns:
            Dictionary containing usage statistics
        """
        total_keywords = len(self.regular_keywords) + len(self.ranking_keywords)
        used_regular = len(self.state.get("used_regular_keywords", []))
        used_ranking = len(self.state.get("used_ranking_keywords", []))
        total_used = len(self.state.get("used_keywords", []))
        
        return {
            "total_keywords": total_keywords,
            "regular_keywords": len(self.regular_keywords),
            "ranking_keywords": len(self.ranking_keywords),
            "used_keywords": total_used,
            "used_regular_keywords": used_regular,
            "used_ranking_keywords": used_ranking,
            "remaining_regular_keywords": len(self.regular_keywords) - used_regular,
            "remaining_ranking_keywords": len(self.ranking_keywords) - used_ranking,
            "current_cycle": self.state.get("current_cycle", 1),
            "total_posts": self.state.get("total_posts", 0),
            "last_updated": self.state.get("last_updated"),
            "last_ranking_keyword_date": self.state.get("last_ranking_keyword_date"),
            "progress_percentage": (total_used / total_keywords * 100) if total_keywords > 0 else 0
        }
    
    def list_remaining_keywords(self) -> Dict[str, List[str]]:
        """
        Get a list of remaining keywords in the current cycle.
        
        Returns:
            Dictionary with 'regular' and 'ranking' keyword lists
        """
        used_regular = set(self.state.get("used_regular_keywords", []))
        used_ranking = set(self.state.get("used_ranking_keywords", []))
        
        return {
            "regular": [kw for kw in self.regular_keywords if kw not in used_regular],
            "ranking": [kw for kw in self.ranking_keywords if kw not in used_ranking]
        }
    
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
        print(f"    Regular Keywords: {stats['regular_keywords']}")
        print(f"    Ranking Keywords: {stats['ranking_keywords']}")
        print(f"  Used Keywords: {stats['used_keywords']}")
        print(f"    Used Regular: {stats['used_regular_keywords']}")
        print(f"    Used Ranking: {stats['used_ranking_keywords']}")
        print(f"  Remaining Keywords:")
        print(f"    Regular: {stats['remaining_regular_keywords']}")
        print(f"    Ranking: {stats['remaining_ranking_keywords']}")
        print(f"  Current Cycle: {stats['current_cycle']}")
        print(f"  Total Posts: {stats['total_posts']}")
        print(f"  Progress: {stats['progress_percentage']:.1f}%")
        print(f"  Last Updated: {stats['last_updated']}")
        print(f"  Last Ranking Keyword: {stats['last_ranking_keyword_date']}")
    
    elif args.list:
        remaining = manager.list_remaining_keywords()
        print(f"Remaining Regular Keywords ({len(remaining['regular'])}):")
        for i, kw in enumerate(remaining['regular'], 1):
            print(f"  {i}. {kw}")
        print(f"\nRemaining Ranking Keywords ({len(remaining['ranking'])}):")
        for i, kw in enumerate(remaining['ranking'], 1):
            print(f"  {i}. {kw}")
    
    elif args.mark_used:
        manager.mark_keyword_used(args.mark_used)
        print(f"Marked as used: {args.mark_used}")
    
    elif args.reset:
        manager._reset_regular_cycle()
        print("Regular keyword cycle reset successfully")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
