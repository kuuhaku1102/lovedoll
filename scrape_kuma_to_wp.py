"""
Scrape product data from https://www.kuma-doll.com/Products/list-r1.html (with pagination)
and post it to a WordPress REST API.

Installation:
    pip install playwright requests beautifulsoup4 lxml
    playwright install chromium

Example usage:
    python scrape_kuma_to_wp.py \
        --url "https://www.kuma-doll.com/Products/list-r1.html" \
        --wp-base "https://freya-era.com" \
        --max-pages 10

WordPress REST endpoints are constructed from the base URL (default: https://freya-era.com):
    ADD:  <wp_base>/wp-json/lovedoll/v1/add-item
    LIST: <wp_base>/wp-json/lovedoll/v1/list

Notes:
    * Timeouts and HTTP error handling are included.
    * Relative URLs are resolved to absolute URLs.
    * Selectors are dedicated to kuma-doll.com (no sweet-doll / happiness-doll / yourdoll selectors are used).
"""
from __future__ import annotations

import argparse
import base64
import logging
import os
import re
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

WP_BASE_DEFAULT = "https://freya-era.com"
DEFAULT_CATEGORY_URL = "https://www.kuma-doll.com/Products/list-r1.html"
MAX_PAGES_DEFAULT = 10
REQUEST_TIMEOUT = 15
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; LovedollScraper/4.0; +https://freya-era.com)",
}

PLAYWRIGHT_WAIT_SELECTOR = "img[src*='image/cache'], img[src*='.webp'], img[src*='.jpg'], img[src*='.jpeg']"
PLAYWRIGHT_WAIT_MS = 12000


def normalize_price(raw_text: str) -> Optional[int]:
    """Convert price text like "274,500円(税込)" to integer 274500."""

    digits = re.findall(r"[0-9]+", raw_text)
    if not digits:
        return None
    try:
        return int("".join(digits))
    except ValueError:
        return None


def _pick_image_src(image_tag, container=None) -> Optional[str]:
    """Pick the best available (non data URI) image URL from lazy-loaded attributes or fallbacks."""

    def srcset_candidates(value: Optional[str]) -> List[str]:
        if not value:
            return []
        urls = []
        for entry in value.split(","):
            url_part = entry.strip().split()[0] if entry.strip() else ""
            if url_part:
                urls.append(url_part)
        # prefer larger (last) candidates first
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
            image_tag.get("data-echo"),
            image_tag.get("data-hires"),
            image_tag.get("data-image"),
            image_tag.get("src"),
        ]
    )

    # Fallback: check for <noscript> image HTML nested near the tag
    if container is not None:
        noscript = image_tag.find_next("noscript")
        if noscript and noscript.string:
            try:
                ns_soup = BeautifulSoup(noscript.string, "lxml")
                ns_img = ns_soup.find("img")
                if ns_img:
                    candidates.extend(srcset_candidates(ns_img.get("srcset")))
                    candidates.append(ns_img.get("src"))
            except Exception:
                pass

        # Absolute fallback: any other <img> inside the same product container
        for extra_img in container.find_all("img"):
            candidates.extend(srcset_candidates(extra_img.get("srcset")))
            candidates.append(extra_img.get("src"))
            candidates.append(extra_img.get("data-src"))

    for candidate in candidates:
        if candidate and not candidate.startswith("data:"):
            return candidate
    return None


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


def parse_item(item_html: str, base_url: str) -> Optional[Dict[str, object]]:
    """Extract title, price, image URL, and product URL from a kuma-doll product block."""

    soup = BeautifulSoup(item_html, "lxml")
    container = soup if soup.name == "div" else soup.find("div", class_="product-item") or soup

    title_tag = container.select_one("a.title")
    image_link = container.select_one("a.image")
    image_tag = container.select_one("a.image img")
    price_tag = container.select_one(".price span")

    link_tag = image_link if image_link and image_link.get("href") else title_tag

    if not (title_tag and image_tag and price_tag and link_tag and link_tag.get("href")):
        return None

    price = normalize_price(price_tag.get_text(" ", strip=True))
    if price is None:
        return None
    if price >= 1_000_000:
        logger.info("Skipping item priced at or above 1,000,000: %s", price)
        return None

    image_src = _pick_image_src(image_tag, container)
    if not image_src:
        return None

    return {
        "title": title_tag.get_text(strip=True),
        "price": price,
        "image_url": urljoin(base_url, image_src),
        "product_url": urljoin(base_url, link_tag.get("href")),
    }


def fetch_detail_image_with_playwright(context, product_url: str, base_url: str) -> Optional[Tuple[str, bytes, str]]:
    """Fetch detail page and real image using Playwright in the same session."""

    page = context.new_page()
    try:
        logger.info("[Playwright] Opening detail page: %s", product_url)
        page.goto(product_url, wait_until="networkidle", timeout=REQUEST_TIMEOUT * 1000)
        try:
            page.wait_for_selector(PLAYWRIGHT_WAIT_SELECTOR, timeout=PLAYWRIGHT_WAIT_MS)
            page.wait_for_timeout(10000)
        except PlaywrightTimeoutError:
            logger.warning("Timeout waiting for images to load on %s", product_url)

        html = page.content()
    finally:
        page.close()

    soup = BeautifulSoup(html, "lxml")
    image_url: Optional[str] = None

    selectors = [
        "div.product img",
        "div#product img",
        "div.product-gallery img",
        "div.product-images img",
        "img",
    ]

    for selector in selectors:
        for img in soup.select(selector):
            candidate = _pick_image_src(img, soup)
            if not candidate:
                continue
            resolved = urljoin(base_url, candidate)
            if resolved and "logo" not in resolved:
                image_url = resolved
                break
        if image_url:
            break

    if not image_url:
        logger.error("Could not locate image on detail page: %s", product_url)
        return None

    try:
        logger.info("[Playwright] Downloading image with session: %s", image_url)
        img_resp = context.request.get(image_url, timeout=REQUEST_TIMEOUT * 1000)
        img_resp.raise_for_status()
        content = img_resp.body()
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to fetch image %s: %s", image_url, exc)
        return None

    filename = os.path.basename(urlsplit(image_url).path) or "kuma-image.webp"
    return image_url, content, filename


def build_page_url(base_url: str, page: int) -> str:
    """Append or replace page query parameter for pagination."""

    if page <= 1:
        return base_url

    parts = urlsplit(base_url)
    query_params = dict((k, v[0]) for k, v in parse_qs(parts.query).items())
    query_params["page"] = str(page)
    new_query = urlencode(query_params, doseq=True)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))


def scrape_items(category_url: str, max_pages: int = MAX_PAGES_DEFAULT, delay: float = 1.0) -> List[Dict[str, object]]:
    """Scrape kuma-doll with Playwright (list -> detail -> image) and return product dictionaries."""

    collected: List[Dict[str, object]] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=HEADERS["User-Agent"])

        for page_num in range(1, max_pages + 1):
            page_url = build_page_url(category_url, page_num)
            page = context.new_page()
            try:
                logger.info("[Playwright] Fetching page: %s", page_url)
                page.goto(page_url, wait_until="networkidle", timeout=REQUEST_TIMEOUT * 1000)
                try:
                    page.wait_for_selector(".product-item", timeout=PLAYWRIGHT_WAIT_MS)
                except PlaywrightTimeoutError:
                    logger.warning("Timeout waiting for product items on %s", page_url)
                page.wait_for_timeout(2000)
                html = page.content()
            finally:
                page.close()

            soup = BeautifulSoup(html, "lxml")
            items = soup.select(".product-item")
            if not items:
                logger.info("No products found on page %s; stopping.", page_url)
                break

            for item in items:
                parsed = parse_item(str(item), category_url)
                if not parsed:
                    continue

                detail = fetch_detail_image_with_playwright(context, parsed["product_url"], category_url)
                if not detail:
                    logger.info("Skipping item; could not fetch detail image: %s", parsed.get("title"))
                    continue

                image_url, image_bytes, filename = detail
                parsed["image_url"] = image_url
                parsed["image_content"] = base64.b64encode(image_bytes).decode("ascii")
                parsed["image_name"] = filename
                collected.append(parsed)

            logger.info("Collected %d items so far", len(collected))

            next_link = soup.select_one("a.next, a.page-link[rel='next']")
            if not next_link and page_num >= max_pages:
                break
            if next_link and next_link.get("href"):
                candidate = urljoin(category_url, next_link.get("href"))
                if candidate != page_url:
                    category_url = candidate
                    continue

            if delay > 0 and page_num < max_pages:
                try:
                    import time

                    time.sleep(delay)
                except Exception:
                    pass

        context.close()
        browser.close()

    return collected


def post_to_wp(data: Dict[str, object], wp_base: str, session: Optional[requests.Session] = None) -> Optional[int]:
    """Post a single product dictionary to the WordPress REST API."""

    close_session = False
    if session is None:
        session = requests.Session()
        close_session = True

    endpoint = urljoin(wp_base.rstrip("/"), "/wp-json/lovedoll/v1/add-item")
    try:
        resp = session.post(endpoint, json=data, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        payload = resp.json()
        post_id = payload.get("id") if isinstance(payload, dict) else None
        logger.info("Posted: %s (ID: %s)", data.get("title"), post_id)
        return post_id
    except requests.RequestException as exc:
        logger.error("Failed to POST %s: %s", data.get("title"), exc)
    except ValueError:
        logger.error("Non-JSON response when posting %s", data.get("title"))
    finally:
        if close_session:
            session.close()
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape kuma-doll category and post to WordPress.")
    parser.add_argument("--url", default=DEFAULT_CATEGORY_URL, help="Category URL to scrape")
    parser.add_argument("--wp-base", default=WP_BASE_DEFAULT, help="Base URL of the WordPress site")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of items to send")
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES_DEFAULT, help="Maximum pages to scrape")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds to wait between pages")
    args = parser.parse_args()

    items = scrape_items(args.url, max_pages=args.max_pages, delay=args.delay)
    if not items:
        logger.warning("No items scraped; exiting")
        raise SystemExit(1)

    session = requests.Session()
    session.headers.update(HEADERS)

    existing_urls = fetch_existing_product_urls(args.wp_base, session=session)
    seen: Set[str] = set(existing_urls)

    sent = 0
    for item in items:
        product_url = item.get("product_url")
        if product_url in seen:
            logger.info("Skipping duplicate product URL: %s", product_url)
            continue
        if args.limit is not None and sent >= args.limit:
            logger.info("Reached limit of %d items", args.limit)
            break
        post_to_wp(item, args.wp_base, session=session)
        seen.add(product_url)
        sent += 1

    session.close()
    logger.info("Finished. Sent %d items", sent)


if __name__ == "__main__":
    main()
