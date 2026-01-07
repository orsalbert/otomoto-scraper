from pathlib import Path
from typing import List
import requests
import urllib3
from tqdm import tqdm
from url_builder import build_search_url
from fetcher import detect_last_page, fetch_html, is_zero_results, polite_sleep
from parser.json_ld_parser import parse_json_ld


def save_html_snapshot(html: str, page: int, output_dir: str, base_args: dict = {}):
    parent_dir = Path.cwd().parent
    full_path = parent_dir / Path(output_dir)
    full_path.mkdir(parents=True, exist_ok=True)
    if base_args:
        path = (
            Path(full_path)
            / f"{base_args['brand'].lower()}_{base_args['model'].lower()}_page_{page}.html"
        )
    else:
        path = Path(full_path) / f"page_{page}.html"
    path.write_text(html, encoding="utf-8")


def iterate_search_pages(
    session: requests.Session,
    base_args: dict = {},
    input_url: str = "",
    max_pages: int = 10,
    save_snapshots: bool = False,
    snapshot_dir: str = "data/html_snapshots",
    disable_tqdm=False,
) -> List[str]:
    """
    Fetch search result pages until stopping condition is met.
    Returns a list of HTML strings (one per page).
    """
    pbar = tqdm(
        desc="Pages fetched",
        unit="page",
        bar_format="{desc}: {n} [{elapsed}, {rate_fmt}]",
        disable=disable_tqdm,
    )

    pages_html = []
    detected_last_page = None

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    for page in range(1, max_pages + 1):

        pbar.update(1)

        if input_url:
            url = input_url + f"&page={page}"
        else:
            url = build_search_url(page=page, **base_args)

        tqdm.write(f"[INFO] Fetching page {page}")

        html = fetch_html(url, session)

        if html is None:
            tqdm.write("[STOP] Fetch failed.")
            break

        if is_zero_results(html):
            tqdm.write("[STOP] Zero results page detected.")
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
                tqdm.write(f"[INFO] Detected last page: {detected_last_page}")

        if detected_last_page is not None and page >= detected_last_page:
            tqdm.write("[STOP] Reached last page.")
            break

        polite_sleep()

    pbar.close()
    return pages_html


if __name__ == "__main__":

    import os
    import pandas as pd
    from parser.graphql_parser import parse_graphql
    from parser.merger import merge_jsonld_and_graphql

    def parse_search_page(html: str) -> list[dict]:
        jsonld = parse_json_ld(html)
        graphql = parse_graphql(html)
        return merge_jsonld_and_graphql(jsonld, graphql)

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

    for car in cars:
        base_args.update(car)

        session = requests.Session()

        pages.extend(
            iterate_search_pages(
                base_args=base_args,
                session=session,
                max_pages=10,
                save_snapshots=save_snapshots,
                snapshot_dir=f"data/html_snapshots/",
            )
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
