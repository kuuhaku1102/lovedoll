#!/usr/bin/env python3
"""
Fetch ranking page titles from WordPress
"""
import requests
import sys

WP_BASE = "https://freya-era.com"
API_ENDPOINT = f"{WP_BASE}/wp-json/wp/v2/website_ranking"

try:
    response = requests.get(API_ENDPOINT, params={"per_page": 100}, timeout=10)
    response.raise_for_status()
    rankings = response.json()
    
    print(f"Found {len(rankings)} ranking pages:")
    for ranking in rankings:
        title = ranking.get("title", {}).get("rendered", "")
        print(f"  - {title}")
        
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
