"""
Scrape product data from https://sweet-doll.com/product-category/sedoll/ (with pagination)
using the site's dedicated HTML structure and post it to a WordPress REST API.

Installation:
    pip install requests beautifulsoup4 lxml

Example usage:
    python scrape_sweet_to_wp.py \
        --url "https://sweet-doll.com/product-category/sedoll/" \
        --wp-base "https://freya-era.com" \
        --max-pages 10

WordPress REST endpoints are constructed from the base URL (default: https://freya-era.com):
    ADD:  <wp_base>/wp-json/lovedoll/v1/add-item
    LIST: <wp_base>/wp-json/lovedoll/v1/list

Notes:
    * Timeouts and HTTP error handling are included.
    * Relative URLs are resolved to absolute URLs.
    * Selectors are dedicated to sweet-doll.com (no yourdoll.jp / happiness-doll.com selectors are used).
"""
from __future__ import annotations

import argparse
import logging
import re
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

WP_BASE_DEFAULT = "https://freya-era.com"
DEFAULT_CATEGORY_URL = "https://sweet-doll.com/product-category/sedoll/"
MAX_PAGES_DEFAULT = 10
REQUEST_TIMEOUT = 15
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; LovedollScraper/3.0; +https://freya-era.com)",
}


def normalize_price(raw_text: str) -> Optional[int]:
    digits = re.findall(r"[0-9]+", raw_text)
    if not digits:
        return None
    try:
        return int("".join(digits))
    except ValueError:
        return None


def parse_item(item_html: str, base_url: str) -> Optional[Dict[str, object]]:
    """Extract title, price, image URL, and product URL from a sweet-doll product block.

    Expected HTML structure:
        <div class="product-grid-item ...">
            <div class="product-wrapper">
                <div class="product-element-top">
                    <a class="product-image-link" href="..."><img src="..."></a>
                </div>
                <div class="product-element-bottom">
                    <h3 class="wd-entities-title"><a href="...">TITLE</a></h3>
                    <span class="price"><span class="woocommerce-Price-amount">163,000円</span></span>
                </div>
            </div>
        </div>
    """

    soup = BeautifulSoup(item_html, "lxml")
    container = soup if soup.name == "div" else soup.find("div", class_="product-grid-item") or soup

    title_tag = container.select_one(".wd-entities-title a")
    image_link = container.select_one(".product-image-link")
    image_tag = container.select_one(".product-image-link img")
    price_tag = container.select_one(".price .woocommerce-Price-amount")

    if not (title_tag and image_tag and price_tag):
        return None

    # Prefer product URL from image link; fallback to title link
    link_tag = image_link if image_link and image_link.get("href") else title_tag
    if not link_tag or not link_tag.get("href"):
        return None

    price = normalize_price(price_tag.get_text(" ", strip=True))
    if price is None:
        return None

    image_src = image_tag.get("src") or image_tag.get("data-src") or image_tag.get("data-original")
    if not image_src:
        return None

    return {
        "title": title_tag.get_text(strip=True),
        "price": price,
        "image_url": urljoin(base_url, image_src),
        "product_url": urljoin(base_url, link_tag.get("href")),
    }


def fetch_existing_product_urls(wp_base: str, session: Optional[requests.Session] = None) -> Set[str]:
    """Fetch existing product URLs from WordPress to avoid duplicates."""

    close_session = False
    if session is None:
        session = requests.Session()
        close_session = True

    endpoint = urljoin(wp_base.rstrip("/"), "/wp-json/lovedoll/v1/list")
    urls: Set[str] = set()

    try:
        resp = session.get(endpoint, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        payload = resp.json()
    except requests.RequestException as exc:
        logger.warning("Could not fetch existing items; duplicate check may be incomplete: %s", exc)
        payload = None
    except ValueError:
        logger.warning("Could not parse existing items (non-JSON response)")
        payload = None

    def collect(entry: dict) -> None:
        for key in ("product_url", "product_link", "url"):
            val = entry.get(key)
            if isinstance(val, str):
                urls.add(val)
                return

    if isinstance(payload, list):
        for entry in payload:
            if isinstance(entry, dict):
                collect(entry)
    elif isinstance(payload, dict):
        items = payload.get("items")
        if isinstance(items, list):
            for entry in items:
                if isinstance(entry, dict):
                    collect(entry)

    if urls:
        logger.info("Loaded %d existing product URLs from WordPress", len(urls))

    if close_session:
        session.close()
    return urls


def scrape_items(category_url: str, max_pages: int = MAX_PAGES_DEFAULT) -> List[Dict[str, object]]:
    """Scrape sweet-doll category pages and return product dictionaries."""

    session = requests.Session()
    session.headers.update(HEADERS)

    results: List[Dict[str, object]] = []
    visited_urls: Set[str] = set()

    current_url = category_url
    for page in range(1, max_pages + 1):
        logger.info("Fetching page %s: %s", page, current_url)
        try:
            resp = session.get(current_url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", current_url, exc)
            break

        soup = BeautifulSoup(resp.text, "lxml")
        items = soup.select("div.product-grid-item")
        logger.info("Found %d products on page", len(items))

        for item in items:
            parsed = parse_item(str(item), current_url)
            if not parsed:
                continue
            if parsed["product_url"] in visited_urls:
                continue
            visited_urls.add(parsed["product_url"])
            results.append(parsed)

        next_link = soup.select_one("a.next.page-numbers") or soup.find("a", rel="next")
        if not next_link or not next_link.get("href"):
            break
        current_url = urljoin(current_url, next_link["href"])

    session.close()
    logger.info("Total products scraped: %d", len(results))
    return results


def post_to_wp(data: Dict[str, object], wp_base: str, session: Optional[requests.Session] = None) -> Optional[int]:
    """Post a single product to WordPress REST API. Returns created ID or None."""

    close_session = False
    if session is None:
        session = requests.Session()
        close_session = True

    endpoint = urljoin(wp_base.rstrip("/"), "/wp-json/lovedoll/v1/add-item")

    try:
        resp = session.post(endpoint, json=data, timeout=REQUEST_TIMEOUT, headers=HEADERS)
        resp.raise_for_status()
        payload = resp.json()
        created_id = payload.get("id") if isinstance(payload, dict) else None
        logger.info("Posted: %s (ID: %s)", data.get("title"), created_id)
        return created_id
    except requests.RequestException as exc:
        logger.error("Failed to post %s: %s", data.get("title"), exc)
    except ValueError:
        logger.error("Failed to parse response for %s", data.get("title"))
    finally:
        if close_session:
            session.close()
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape sweet-doll.com category pages and post to WordPress.")
    parser.add_argument("--url", default=DEFAULT_CATEGORY_URL, help="Category URL to scrape (default: %(default)s)")
    parser.add_argument("--wp-base", default=WP_BASE_DEFAULT, help="WordPress base URL (default: %(default)s)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of items to post")
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES_DEFAULT, help="Max pages to scrape")

    args = parser.parse_args()

    session = requests.Session()
    session.headers.update(HEADERS)

    existing_urls = fetch_existing_product_urls(args.wp_base, session=session)
    items = scrape_items(args.url, max_pages=args.max_pages)

    posted = 0
    for item in items:
        if args.limit is not None and posted >= args.limit:
            break
        if item["product_url"] in existing_urls:
            logger.info("Skipping duplicate product_url: %s", item["product_url"])
            continue
        post_to_wp(item, args.wp_base, session=session)
        posted += 1

    session.close()
    logger.info("Completed posting %d items", posted)


if __name__ == "__main__":
    main()
