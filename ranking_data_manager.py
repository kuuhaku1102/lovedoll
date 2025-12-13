#!/usr/bin/env python3
"""
Ranking Data Manager

This module fetches ranking data (titles and affiliate links) from WordPress
and provides them for use in blog post generation.

Features:
    - Fetch ranking data from WordPress REST API
    - Cache ranking data locally
    - Map keywords to affiliate links
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

WP_BASE_DEFAULT = "https://freya-era.com"
CACHE_FILE = Path(__file__).parent / "ranking_cache.json"
CACHE_DURATION_HOURS = 24  # Cache for 24 hours


class RankingDataManager:
    """Manage ranking data from WordPress."""
    
    def __init__(self, wp_base: str = None):
        """
        Initialize the ranking data manager.
        
        Args:
            wp_base: WordPress base URL
        """
        self.wp_base = (wp_base or os.getenv("WP_BASE_URL", WP_BASE_DEFAULT)).rstrip("/")
        self.api_endpoint = f"{self.wp_base}/wp-json/wp/v2/website_ranking"
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """Load cached ranking data."""
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    
                # Check if cache is still valid
                cached_time = datetime.fromisoformat(cache.get("cached_at", "2000-01-01"))
                if datetime.now() - cached_time < timedelta(hours=CACHE_DURATION_HOURS):
                    logger.info(f"Loaded ranking cache: {len(cache.get('rankings', []))} items")
                    return cache
                else:
                    logger.info("Cache expired, will fetch new data")
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
        
        return {"rankings": [], "cached_at": None}
    
    def _save_cache(self):
        """Save ranking data to cache."""
        try:
            self.cache["cached_at"] = datetime.now().isoformat()
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved ranking cache: {len(self.cache['rankings'])} items")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def fetch_rankings(self, force_refresh: bool = False) -> List[Dict]:
        """
        Fetch ranking data from WordPress.
        
        Args:
            force_refresh: Force refresh even if cache is valid
            
        Returns:
            List of ranking data dictionaries
        """
        # Use cache if available and not forcing refresh
        if not force_refresh and self.cache.get("rankings"):
            logger.info("Using cached ranking data")
            return self.cache["rankings"]
        
        logger.info(f"Fetching ranking data from {self.api_endpoint}")
        
        try:
            response = requests.get(
                self.api_endpoint,
                params={"per_page": 100, "status": "publish"},
                timeout=15
            )
            response.raise_for_status()
            
            rankings_raw = response.json()
            rankings = []
            
            for item in rankings_raw:
                # Extract title
                title = item.get("title", {})
                if isinstance(title, dict):
                    title = title.get("rendered", "")
                
                # Extract affiliate link from meta
                affiliate_link = ""
                if "meta" in item:
                    affiliate_link = item["meta"].get("_ranking_affiliate_link", "")
                
                # Extract rating
                rating = ""
                if "meta" in item:
                    rating = item["meta"].get("_ranking_rating", "")
                
                ranking_data = {
                    "id": item.get("id"),
                    "title": title,
                    "affiliate_link": affiliate_link,
                    "rating": rating,
                    "permalink": item.get("link", "")
                }
                
                rankings.append(ranking_data)
                logger.info(f"Fetched: {title} -> {affiliate_link}")
            
            # Update cache
            self.cache["rankings"] = rankings
            self._save_cache()
            
            logger.info(f"Successfully fetched {len(rankings)} ranking items")
            return rankings
            
        except Exception as e:
            logger.error(f"Failed to fetch ranking data: {e}")
            # Return cached data if available
            if self.cache.get("rankings"):
                logger.warning("Using stale cache due to fetch error")
                return self.cache["rankings"]
            return []
    
    def get_affiliate_link_for_keyword(self, keyword: str) -> Optional[Dict]:
        """
        Get affiliate link information for a specific keyword.
        
        Args:
            keyword: The keyword to search for (e.g., "Sweet Doll おすすめ")
            
        Returns:
            Dictionary with title and affiliate_link, or None if not found
        """
        rankings = self.fetch_rankings()
        
        # Extract the brand name from keyword
        # e.g., "Sweet Doll おすすめ" -> "Sweet Doll"
        brand_name = keyword.split()[0:2]  # Take first two words
        if len(brand_name) == 2:
            brand_name = " ".join(brand_name)
        else:
            brand_name = keyword.split()[0]
        
        logger.info(f"Searching for brand: {brand_name} in keyword: {keyword}")
        
        # Search for matching ranking
        for ranking in rankings:
            title = ranking.get("title", "")
            if brand_name.lower() in title.lower():
                logger.info(f"Found match: {title} -> {ranking.get('affiliate_link')}")
                return {
                    "title": title,
                    "affiliate_link": ranking.get("affiliate_link", ""),
                    "rating": ranking.get("rating", ""),
                    "permalink": ranking.get("permalink", "")
                }
        
        logger.warning(f"No affiliate link found for keyword: {keyword}")
        return None
    
    def get_all_ranking_keywords(self) -> List[str]:
        """
        Get all possible keywords based on ranking titles.
        
        Returns:
            List of keywords
        """
        rankings = self.fetch_rankings()
        keywords = []
        
        suffixes = ["おすすめ", "レビュー", "評判", "購入ガイド", "口コミ"]
        
        for ranking in rankings:
            title = ranking.get("title", "")
            for suffix in suffixes:
                keyword = f"{title} {suffix}"
                keywords.append(keyword)
        
        return keywords


def main():
    """Main function for testing."""
    import argparse
    
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    
    parser = argparse.ArgumentParser(description="Ranking Data Manager")
    parser.add_argument("--fetch", action="store_true", help="Fetch ranking data")
    parser.add_argument("--refresh", action="store_true", help="Force refresh cache")
    parser.add_argument("--search", type=str, help="Search for keyword")
    parser.add_argument("--list", action="store_true", help="List all rankings")
    
    args = parser.parse_args()
    
    manager = RankingDataManager()
    
    if args.fetch or args.refresh:
        rankings = manager.fetch_rankings(force_refresh=args.refresh)
        print(f"Fetched {len(rankings)} ranking items")
        for r in rankings:
            print(f"  - {r['title']}: {r['affiliate_link']}")
    
    elif args.search:
        result = manager.get_affiliate_link_for_keyword(args.search)
        if result:
            print(f"Found: {result['title']}")
            print(f"Link: {result['affiliate_link']}")
            print(f"Rating: {result['rating']}")
        else:
            print("Not found")
    
    elif args.list:
        rankings = manager.fetch_rankings()
        print(f"All Rankings ({len(rankings)}):")
        for r in rankings:
            print(f"  - {r['title']}")
            print(f"    Link: {r['affiliate_link']}")
            print(f"    Rating: {r['rating']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
