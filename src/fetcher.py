import time
import requests
import random
from bs4 import BeautifulSoup
from typing import Optional
from url_builder import build_search_url
import re

# from parser.json_ld_parser import parse_search_page

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Connection": "keep-alive",
}


def fetch_html(
    url: str,
    session: requests.Session,
    timeout: int = 15,
) -> Optional[str]:
    try:
        response = session.get(url, headers=HEADERS, timeout=timeout, verify=False)
        response.raise_for_status()
        return response.text

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return None


def is_zero_results(html: str) -> bool:
    zero_markers = [
        "Niczego nie znaleźliśmy",
        "Nie znaleźliśmy",
        "Brak wyników",
        "0 ogłoszeń",
    ]

    html_lower = html.lower()
    return any(marker.lower() in html_lower for marker in zero_markers)


# def detect_last_page(html: str) -> int:
def detect_last_page(html: str):
    soup = BeautifulSoup(html, "html.parser")

    og_url_tag = soup.find("meta", property="og:url")

    if og_url_tag and "content" in og_url_tag.attrs:
        og_url = og_url_tag["content"]
        match = re.search(r"page=(\d+)", og_url)
        if match:
            return int(match.group(1))

    return og_url


def polite_sleep(min_seconds: float = 1.0, max_seconds: float = 2.0):
    time.sleep(random.uniform(min_seconds, max_seconds))


if __name__ == "__main__":
    session = requests.Session()

    url = build_search_url(
        brand="Renault",
        model="Kadjar",
        year_from=2019,
        price_from=50000,
        price_to=75000,
        year_to=2022,
        mileage_to=150000,
        fuel_type="petrol",
        gearbox="manual",
        accident_free=True,
        page=4,
    )

    html = fetch_html(url, session)

    print(detect_last_page(html))
    # if html is None:
    #     print("No HTML fetched.")
    # else:
    #     print("Zero results:", is_zero_results(html))
    #     print("Last page:", detect_last_page(html))

    # for posting in parse_search_page(html):
    #     print(posting)

    # soup = BeautifulSoup(html, "lxml")

    # page_numbers = []

    # print(soup)
