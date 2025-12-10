"""
Scrape product data from a category page (including pagination) and post it to a WordPress REST API.

Requirements installation:
    pip install requests beautifulsoup4 lxml

Usage:
    python scrape_to_wp.py --url "https://yourdoll.jp/product-category/all-sex-dolls/" --wp-base "https://freya-era.com"

Defaults:
    - Category URL: https://yourdoll.jp/product-category/all-sex-dolls/
    - Pagination: up to 10 pages (override with --max-pages)

WordPress REST endpoints are constructed from the base URL (default: https://freya-era.com):
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

WP_BASE_DEFAULT = "https://freya-era.com"
DEFAULT_CATEGORY_URL = "https://yourdoll.jp/product-category/all-sex-dolls/"
MAX_PAGES = 10
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; LovedollScraper/1.0; +https://freya-era.com)"
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


def _pick_image_src(image_tag) -> Optional[str]:
    """Pick the best available image URL from lazy-loaded attributes."""

    def from_srcset(value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        # srcset values are separated by commas and can include descriptors like "400w"
        first_entry = value.split(",")[0].strip()
        # Each entry can be "url 400w"; keep only the URL part
        return first_entry.split()[0] if first_entry else None

    return (
        image_tag.get("src")
        or image_tag.get("data-lazy-src")
        or image_tag.get("data-src")
        or from_srcset(image_tag.get("data-lazy-srcset"))
        or from_srcset(image_tag.get("data-srcset"))
        or from_srcset(image_tag.get("srcset"))
    )


def _find_image_tag(root: BeautifulSoup) -> Optional[object]:
    """Locate an <img> tag, including inside <noscript>, for a product block."""

    tag = root.select_one(".product-image-link img")
    if tag:
        return tag

    # Some themes wrap the real <img> inside a <noscript> block; parse its content.
    noscript = root.select_one(".product-image-link noscript")
    if noscript:
        inner = BeautifulSoup(noscript.decode_contents(), "lxml")
        return inner.find("img")

    return None


def parse_item(item_html: str, base_url: str) -> Optional[Dict[str, object]]:
    """Extract title, price, image URL, and product URL from a product block."""
    soup = BeautifulSoup(item_html, "lxml")

    title_tag = soup.select_one("h3.wd-entities-title a")
    price_tag = soup.select_one("span.price") or soup.select_one("span.woocommerce-Price-amount")
    image_tag = _find_image_tag(soup)
    product_link_tag = soup.select_one("a.product-image-link") or title_tag

    if not title_tag or not price_tag or not image_tag or not product_link_tag:
        logger.debug("Skipping item due to missing data")
        return None

    title = title_tag.get_text(strip=True)
    price = normalize_price(price_tag.get_text(" ", strip=True))
    image_src = _pick_image_src(image_tag)
    product_href = product_link_tag.get("href")

    if price is None or not image_src or not product_href:
        logger.debug("Skipping item due to unparsable price or image")
        return None

    image_url = urljoin(base_url, image_src)
    product_url = urljoin(base_url, product_href)

    return {
        "title": title,
        "price": price,
        "image_url": image_url,
        "product_url": product_url,
        "product_link": product_url,
    }


def scrape_items(url: str, max_pages: int = MAX_PAGES) -> List[Dict[str, object]]:
    """Scrape a category page (following pagination) and return product dictionaries."""
    session = requests.Session()
    session.headers.update(HEADERS)

    items: List[Dict[str, object]] = []
    next_url: Optional[str] = url
    page_count = 0

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

        page_count += 1
        if page_count >= max_pages:
            logger.info("Reached max page limit (%d); stopping pagination", max_pages)
            break

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
    parser.add_argument(
        "--url",
        default=DEFAULT_CATEGORY_URL,
        help="Category URL to scrape (default: https://yourdoll.jp/product-category/all-sex-dolls/)",
    )
    parser.add_argument(
        "--wp-base",
        default=WP_BASE_DEFAULT,
        help="WordPress base URL (default: https://freya-era.com)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit on number of products to post",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=MAX_PAGES,
        help="Maximum number of pages to paginate through (default: 10)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    items = scrape_items(args.url, max_pages=args.max_pages)
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
