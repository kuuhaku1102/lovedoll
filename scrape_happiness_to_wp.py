"""
Scrape product data from https://happiness-doll.com/products/list (with pagination)
using the site's dedicated HTML structure and post it to a WordPress REST API.

Requirements installation:
    pip install requests beautifulsoup4 lxml

Usage example:
    python scrape_happiness_to_wp.py \
        --url "https://happiness-doll.com/products/list" \
        --wp-base "https://freya-era.com" \
        --max-pages 10

WordPress REST endpoints are constructed from the base URL (default: https://freya-era.com):
    ADD:  <wp_base>/wp-json/lovedoll/v1/add-item
    LIST: <wp_base>/wp-json/lovedoll/v1/list

Notes:
    * No authentication is assumed (permission_callback = __return_true).
    * Timeouts and HTTP error handling are included.
    * Relative URLs are resolved to absolute URLs.
    * Selectors are dedicated to happiness-doll.com (no yourdoll.jp selectors are used).
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

WP_BASE_DEFAULT = "https://freya-era.com"
DEFAULT_CATEGORY_URL = "https://happiness-doll.com/products/list"
MAX_PAGES = 10
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; LovedollScraper/2.0; +https://freya-era.com)",
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
    """Pick the best available (non data URI) image URL from lazy-loaded attributes."""

    def srcset_candidates(value: Optional[str]) -> List[str]:
        if not value:
            return []
        urls = []
        for entry in value.split(","):
            url_part = entry.strip().split()[0] if entry.strip() else ""
            if url_part:
                urls.append(url_part)
        # Prefer the last (often highest resolution) entry first
        return list(reversed(urls))

    candidates: List[str] = []
    candidates.extend(srcset_candidates(image_tag.get("data-lazy-srcset")))
    candidates.extend(srcset_candidates(image_tag.get("data-srcset")))
    candidates.extend(srcset_candidates(image_tag.get("srcset")))
    candidates.extend(
        [
            image_tag.get("data-lazy-src"),
            image_tag.get("data-src"),
            image_tag.get("data-original"),
            image_tag.get("data-ll-src"),
            image_tag.get("data-cfsrc"),
            image_tag.get("src"),
        ]
    )

    for candidate in candidates:
        if candidate and not candidate.startswith("data:"):
            return candidate
    return None


def _find_image_tag(root: BeautifulSoup) -> Optional[object]:
    """Locate an <img> tag, including inside <noscript>, for a product block."""

    tag = root.find("img")
    if tag:
        return tag

    noscript = root.find("noscript")
    if noscript:
        inner = BeautifulSoup(noscript.decode_contents(), "lxml")
        return inner.find("img")

    return None


def fetch_existing_product_urls(wp_base: str, session: Optional[requests.Session] = None) -> set:
    """Fetch existing product URLs from the WordPress list endpoint to avoid duplicates."""

    close_session = False
    if session is None:
        session = requests.Session()
        close_session = True

    endpoint = urljoin(wp_base.rstrip("/"), "/wp-json/lovedoll/v1/list")
    urls: set[str] = set()

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


def parse_item(item_html: str, base_url: str) -> Optional[Dict[str, object]]:
    """Extract title, price, image URL, and product URL from a happiness-doll block."""

    soup = BeautifulSoup(item_html, "lxml")
    container = soup if soup.name == "li" else soup.find("li", class_="ec-shelfGrid__item") or soup

    link_tag = container.find("a", href=True)
    title_tag = container.select_one(".ec-shelfGrid__item-title")
    image_tag = container.select_one(".ec-shelfGrid__item-image img")

    price_tag = None
    for selector in (".discount-price", ".price-flash", ".price02", ".price"):
        tag = container.select_one(selector)
        if tag:
            price_tag = tag
            break

    if not (link_tag and title_tag and image_tag and price_tag):
        return None

    price = normalize_price(price_tag.get_text(" ", strip=True))
    image_src = _pick_image_src(image_tag)
    if price is None or not image_src:
        return None

    if price >= 1_000_000:
        logger.info("Skipping item priced at or above 1,000,000: %s", price)
        return None

    image_url = urljoin(base_url, image_src)
    product_url = urljoin(base_url, link_tag.get("href"))

    return {
        "title": title_tag.get_text(strip=True),
        "price": price,
        "image_url": image_url,
        "product_url": product_url,
    }


def scrape_items(url: str, max_pages: int = MAX_PAGES, delay: float = 1.5) -> List[Dict[str, object]]:
    """Scrape happiness-doll pages following pagination and return product dictionaries."""

    session = requests.Session()
    session.headers.update(HEADERS)

    items: List[Dict[str, object]] = []
    next_url: Optional[str] = url
    page_count = 0
    seen_product_urls: set[str] = set()

    while next_url and page_count < max_pages:
        logger.info("Fetching page: %s", next_url)
        try:
            resp = session.get(next_url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", next_url, exc)
            break

        time.sleep(max(delay, 0))
        soup = BeautifulSoup(resp.text, "lxml")
        product_nodes = soup.select("li.ec-shelfGrid__item")
        logger.info("Found %d products on page", len(product_nodes))

        for node in product_nodes:
            parsed = parse_item(str(node), base_url=next_url)
            if not parsed:
                continue

            product_url = parsed.get("product_url")
            if product_url in seen_product_urls:
                logger.info("Skipping duplicate product URL already seen in this run: %s", product_url)
                continue

            seen_product_urls.add(product_url)  # type: ignore[arg-type]
            items.append(parsed)

        page_count += 1
        if page_count >= max_pages:
            logger.info("Reached max page limit (%d); stopping pagination", max_pages)
            break

        next_link = soup.select_one("a[rel='next'], .ec-blockPagination__next a, li.ec-blockPagination__next a, a.ec-blockPagination__next")
        if next_link and next_link.get("href"):
            next_url = urljoin(next_url, next_link["href"])
        else:
            next_url = None

    logger.info("Total products scraped: %d", len(items))
    session.close()
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
    parser = argparse.ArgumentParser(description="Scrape products and post to WordPress API (happiness-doll.com)")
    parser.add_argument(
        "--url",
        default=DEFAULT_CATEGORY_URL,
        help="Category URL to scrape (default: https://happiness-doll.com/products/list)",
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
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Seconds to wait after each page fetch (to allow lazy content to load in HTML)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    session = requests.Session()
    session.headers.update(HEADERS)
    existing_urls = fetch_existing_product_urls(args.wp_base, session=session)

    items = scrape_items(args.url, max_pages=args.max_pages, delay=args.delay)
    if not items:
        logger.warning("No items scraped; exiting")
        return 1

    posted = 0
    for item in items:
        if args.limit is not None and posted >= args.limit:
            break

        product_url = item.get("product_url")
        if product_url in existing_urls:
            logger.info("Skipping duplicate product already existing on WordPress: %s", product_url)
            continue

        if post_to_wp(item, wp_base=args.wp_base, session=session) is not None:
            posted += 1
            if product_url:
                existing_urls.add(product_url)

    session.close()

    logger.info("Posted %d/%d items", posted, len(items))
    return 0 if posted else 1


if __name__ == "__main__":
    sys.exit(main())
