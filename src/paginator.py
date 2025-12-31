from parser.json_ld_parser import parse_json_ld
from parser.graphql_parser import parse_graphql
from parser.merger import merge_jsonld_and_graphql
from pathlib import Path
import os
from typing import List
import requests
import pandas as pd

from fetcher import detect_last_page, fetch_html, is_zero_results, polite_sleep
from url_builder import build_search_url


def save_html_snapshot(base_args: dict, html: str, page: int, output_dir: str):
    parent_dir = Path.cwd().parent
    full_path = parent_dir / Path(output_dir)
    full_path.mkdir(parents=True, exist_ok=True)
    path = (
        Path(full_path)
        / f"{base_args['brand'].lower()}_{base_args['model'].lower()}_page_{page}.html"
    )
    path.write_text(html, encoding="utf-8")


def parse_search_page(html: str) -> list[dict]:
    jsonld = parse_json_ld(html)
    graphql = parse_graphql(html)
    return merge_jsonld_and_graphql(jsonld, graphql)


def iterate_search_pages(
    base_args: dict,
    session: requests.Session,
    max_pages: int = 10,
    save_snapshots: bool = False,
    snapshot_dir: str = "data/html_snapshots",
) -> List[str]:
    """
    Fetch search result pages until stopping condition is met.
    Returns a list of HTML strings (one per page).
    """

    pages_html = []
    detected_last_page = None

    for page in range(1, max_pages + 1):
        url = build_search_url(page=page, **base_args)
        print(f"[INFO] Fetching page {page}: {url}")

        html = fetch_html(url, session)

        if html is None:
            print("[STOP] Fetch failed.")
            break

        if is_zero_results(html):
            print("[STOP] Zero results page detected.")
            break

        # Detect last page
        if detected_last_page is None:
            json_list = parse_json_ld(html)

            if json_list:

                if save_snapshots:
                    save_html_snapshot(
                        base_args=base_args,
                        html=html,
                        page=page,
                        output_dir=snapshot_dir,
                    )
                pages_html.append(html)

            else:
                detected_last_page = detect_last_page(html) - 1
                print(f"[INFO] Detected last page: {detected_last_page}")

        if detected_last_page is not None and page >= detected_last_page:
            print("[STOP] Reached last page.")
            break

        polite_sleep()

    return pages_html


if __name__ == "__main__":

    save_snapshots = input("Save HTML snapshots? (y/n): ").strip().lower() == "y"

    cars = [
        {"brand": "Volkswagen", "model": "Taigo"},
        {"brand": "Seat", "model": "Ateca"},
        {"brand": "Ford", "model": "Kuga"},
        {"brand": "Skoda", "model": "Kamiq"},
        {"brand": "Renault", "model": "Kadjar"},
        {"brand": "Suzuki", "model": "SX4-S-Cross"},
        # {"brand": "Honda", "model": "HR-V"},
    ]

    base_args = {
        "year_from": 2019,
        "price_from": 50000,
        "price_to": 75000,
        "year_to": 2022,
        "mileage_to": 150000,
        "fuel_type": "petrol",
        "gearbox": "manual",
        "accident_free": True,
    }

    pages = []

    for model in cars:
        base_args.update(model)

        session = requests.Session()

        pages += iterate_search_pages(
            base_args=base_args,
            session=session,
            max_pages=10,
            save_snapshots=save_snapshots,
            snapshot_dir=f"data/html_snapshots/",
        )

    print(f"\n[RESULT] Collected {len(pages)} pages.")

    # Parse JSON-LD
    listings = []
    for page in pages:
        listings += parse_search_page(page)

    print(f"Parsed {len(listings)} listings")

    df = pd.DataFrame(listings)

    # Save to CSV
    if os.path.exists("listings.csv"):
        # Check if file is empty
        if os.path.getsize("listings.csv") == 0:
            df.to_csv(
                "../data/raw_csv/listings.csv", mode="w", header=True, index=False
            )
        else:
            df.to_csv(
                "../data/raw_csv/listings.csv", mode="a", header=False, index=False
            )
    else:
        df.to_csv("../data/raw_csv/listings.csv", mode="w", header=True, index=False)
    print("Saved to listings.csv")
