from datetime import date, datetime
import json
import pandas as pd
import requests
from pathlib import Path
import urllib3
import subprocess
import os
from tqdm import tqdm

from paginator import iterate_search_pages
from parser.json_ld_parser import parse_json_ld
from parser.graphql_parser import parse_graphql
from parser.merger import merge_jsonld_and_graphql
from normalizer import normalize_dataframe

# Check if tqdm should be used based on environment variable
disable_tqdm = os.environ.get("USE_TQDM", "1") != "1"

# Define the project directory and script path
project_dir = Path.cwd().parent
scraper_script = project_dir / Path("src/run_scraper.py")

# Start the scraper script as a background process
with open(project_dir / "logs/scraper.log", "a") as log:
    subprocess.Popen(
        ["python", str(scraper_script)],
        stdout=log,
        stderr=log,
    )

print(f"Started at {datetime.utcnow().isoformat()}", flush=True)

base_dir = Path.cwd().parent
config_path = base_dir / Path("data/json_parm/config.json")
snapshot_dir = base_dir / Path("data/html_snapshots")
raw_csv_dir = base_dir / Path("data/raw_csv")
processed_csv_dir = base_dir / Path("data/processed_csv")


def parse_search_page(html: str) -> list[dict]:
    jsonld = parse_json_ld(html)
    graphql = parse_graphql(html)
    return merge_jsonld_and_graphql(jsonld, graphql)


def main():

    global input_url, save_snapshots

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session = requests.Session()

    pages = []

    if input_url:
        print(f"[INFO] Scraping single URL: {input_url}", flush=True)

        pages.extend(
            iterate_search_pages(
                base_args={},
                session=session,
                max_pages=20,
                input_url=input_url,
                save_snapshots=save_snapshots,
                snapshot_dir=snapshot_dir,
            )
        )

    else:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        print(
            f"[INFO] Loaded config.json: {len(config)} keys",
            flush=True,
        )

        cars = config["cars"]
        base_args = config["base_args"]

        for car in tqdm(
            cars, desc="Scraping models", leave=False, disable=disable_tqdm
        ):
            args = base_args.copy()
            args.update(car)

            tqdm.write(f"\n[INFO] Scraping car: {car['brand']} {car['model']}")

            if disable_tqdm:
                print(f"[Processing {car['brand']} {car['model']}]", flush=True)

            pages.extend(
                iterate_search_pages(
                    base_args=args,
                    session=session,
                    max_pages=10,
                    input_url=input_url,
                    save_snapshots=save_snapshots,
                    snapshot_dir=snapshot_dir,
                    disable_tqdm=disable_tqdm,
                )
            )

    print(f"\n[INFO] Collected {len(pages)} pages.", flush=True)

    listings = []
    for page in tqdm(pages, desc="Parsing listings"):
        listings.extend(parse_search_page(page))

    print(f"\n[INFO] Parsed {len(listings)} listings.", flush=True)

    df_raw = pd.DataFrame(listings)
    today = date.today().strftime("%Y%m%d")

    raw_csv_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_csv_dir / f"raw_listings_{today}.csv"

    df_raw.to_csv(raw_path, index=False)
    print(f"[INFO] Raw listings saved: {raw_path}", flush=True)

    # Normalize data
    df_processed = normalize_dataframe(df_raw)

    processed_csv_dir.mkdir(parents=True, exist_ok=True)
    processed_path = processed_csv_dir / f"processed_listings_{today}.csv"

    df_processed.to_csv(processed_path, index=False)
    print(f"[INFO] Processed listings saved: {processed_path}", flush=True)

    print(f"[INFO] Done at {datetime.utcnow().isoformat()}", flush=True)


if __name__ == "__main__":

    input_url = ""
    if input_url:
        print("[INFO] Input URL received", flush=True)

    input_snapshot = "n"  # For automated runs, default to 'n'
    save_snapshots = input_snapshot.strip().lower() == "y"
    print(f"[INFO] HTML Snapshots will be saved: {save_snapshots}", flush=True)

    main()
