"""
Scrape product data from a category page (including pagination) and post it to a WordPress REST API.

Requirements installation:
    pip install requests beautifulsoup4 lxml

Usage:
    python scrape_to_wp.py --url "https://yourdoll.jp/product-category/all-sex-dolls/" --wp-base "https://example.com"

WordPress REST endpoints are constructed from the base URL:
    ADD:  <wp_base>/wp-json/lovedoll/v1/add-item
    LIST: <wp_base>/wp-json/lovedoll/v1/list

Notes:
    * No authentication is assumed (permission_callback = __return_true).
    * Timeouts and HTTP error handling are included.
    * Relative URLs are resolved to absolute URLs.
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; LovedollScraper/1.0; +https://example.com)"
}
REQUEST_TIMEOUT = 15


def normalize_price(raw_text: str) -> Optional[int]:
    """Convert price text like "44,650円" to integer 44650."""
    digits = re.findall(r"[0-9]+", raw_text)
    if not digits:
        return None
    try:
        return int("".join(digits))
    except ValueError:
        return None


def parse_item(item_html: str, base_url: str) -> Optional[Dict[str, object]]:
    """Extract title, price, and image URL from a single product block."""
    soup = BeautifulSoup(item_html, "lxml")

    title_tag = soup.select_one("h3.wd-entities-title a")
    price_tag = soup.select_one("span.price") or soup.select_one("span.woocommerce-Price-amount")
    image_tag = soup.select_one(".product-image-link img")

    if not title_tag or not price_tag or not image_tag:
        logger.debug("Skipping item due to missing data")
        return None

    title = title_tag.get_text(strip=True)
    price = normalize_price(price_tag.get_text(" ", strip=True))
    image_src = image_tag.get("src") or image_tag.get("data-lazy-src") or image_tag.get("data-src")

    if price is None or not image_src:
        logger.debug("Skipping item due to unparsable price or image")
        return None

    image_url = urljoin(base_url, image_src)

    return {
        "title": title,
        "price": price,
        "image_url": image_url,
    }


def scrape_items(url: str) -> List[Dict[str, object]]:
    """Scrape a category page (following pagination) and return product dictionaries."""
    session = requests.Session()
    session.headers.update(HEADERS)

    items: List[Dict[str, object]] = []
    next_url: Optional[str] = url

    while next_url:
        logger.info("Fetching page: %s", next_url)
        try:
            resp = session.get(next_url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", next_url, exc)
            break

        soup = BeautifulSoup(resp.text, "lxml")
        product_nodes = soup.select("div.product-grid-item")
        logger.info("Found %d products on page", len(product_nodes))

        for node in product_nodes:
            parsed = parse_item(str(node), base_url=next_url)
            if parsed:
                items.append(parsed)

        # Find next page link
        next_link = soup.select_one("a.next.page-numbers, a[rel='next']")
        if next_link and next_link.get("href"):
            next_url = urljoin(next_url, next_link["href"])
        else:
            next_url = None

    logger.info("Total products scraped: %d", len(items))
    return items


def post_to_wp(data: Dict[str, object], wp_base: str, session: Optional[requests.Session] = None) -> Optional[int]:
    """Send a product dictionary to the WordPress REST endpoint.

    Returns the created item's ID when available.
    """
    close_session = False
    if session is None:
        session = requests.Session()
        close_session = True

    endpoint = urljoin(wp_base.rstrip("/"), "/wp-json/lovedoll/v1/add-item")

    try:
        resp = session.post(endpoint, json=data, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Failed to post to WordPress: %s", exc)
        if close_session:
            session.close()
        return None

    try:
        payload = resp.json()
    except ValueError:
        logger.error("Unexpected response (not JSON): %s", resp.text[:200])
        if close_session:
            session.close()
        return None

    item_id = payload.get("id")
    logger.info("Posted '%s' (ID: %s)", data.get("title"), item_id)

    if close_session:
        session.close()
    return item_id


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape products and post to WordPress API")
    parser.add_argument("--url", required=True, help="Category URL to scrape")
    parser.add_argument("--wp-base", required=True, help="WordPress base URL (e.g., https://example.com)")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit on number of products to post",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    items = scrape_items(args.url)
    if not items:
        logger.warning("No items scraped; exiting")
        return 1

    session = requests.Session()
    session.headers.update(HEADERS)

    posted = 0
    for item in items:
        if args.limit is not None and posted >= args.limit:
            break
        if post_to_wp(item, wp_base=args.wp_base, session=session) is not None:
            posted += 1

    session.close()

    logger.info("Posted %d/%d items", posted, len(items))
    return 0 if posted else 1


if __name__ == "__main__":
    sys.exit(main())
