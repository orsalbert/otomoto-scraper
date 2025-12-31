import json
import re
from bs4 import BeautifulSoup
import os


def find_props_script(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    for script in soup.find_all("script"):
        if script.string and '"props"' in script.string:
            return script.string

    raise RuntimeError("Props script not found")


def extract_urql_state(next_data: dict) -> dict:
    return next_data.get("props", {}).get("pageProps", {}).get("urqlState", {})


def find_advert_search_state(urql_state: dict) -> dict:
    for entry in urql_state.values():
        data_str = entry.get("data")
        if isinstance(data_str, str) and "advertSearch" in data_str:
            return entry

    raise RuntimeError("advertSearch state not found")


def decode_graphql_data(entry: dict) -> dict:
    raw = entry["data"]  # string with backslashes
    return json.loads(raw)  # second decode


def safe_price(advert):
    try:
        return float(advert["price"]["amount"]["value"])
    except (ValueError, TypeError):
        return 0


def correct_polish_letters(st):

    if st is None:
        return ""

    pol = {
        "ą": "a",
        "ć": "c",
        "ę": "e",
        "ł": "l",
        "ń": "n",
        "ó": "o",
        "ś": "s",
        "ź": "z",
        "ż": "z",
    }
    return "".join([pol[c.lower()] if c.lower() in pol else c for c in st])


def extract_listings_from_graphql(graphql_json: dict) -> list[dict]:
    edges = graphql_json["advertSearch"]["edges"]
    listings = []

    for edge in edges:
        advert = edge["node"]

        params = {p["key"]: p.get("value") for p in advert.get("parameters", [])}
        parm_country = {
            p["key"]: p.get("displayValue") for p in advert.get("parameters", [])
        }
        misc = {
            p["name"]: p.get("validity") for p in advert.get("valueAddedServices", [])
        }

        listings.append(
            {
                "id": advert["id"],
                "title": advert["title"],
                "date_added": advert["createdAt"],
                "short_description": correct_polish_letters(advert["shortDescription"]),
                "url": advert["url"],
                "seller_name": correct_polish_letters(advert["sellerLink"]["name"]),
                "seller_site": advert["sellerLink"]["websiteUrl"],
                "brand": params.get("make"),
                "model": params.get("model"),
                "version": params.get("version"),
                "price": safe_price(advert),
                "currency": advert["price"]["amount"]["currencyCode"],
                "year": int(params.get("year", 0)),
                "fuel_type": params.get("fuel_type"),
                "mileage": int(params.get("mileage", 0)),
                "gearbox": params.get("gearbox"),
                "country_code": params.get("country_origin"),
                "country_origin": correct_polish_letters(
                    parm_country.get("country_origin")
                ),
                "engine_capacity": int(params.get("engine_capacity", 0)),
                "engine_power": int(params.get("engine_power", 0)),
                "city": correct_polish_letters(advert["location"]["city"]["name"]),
                "region": correct_polish_letters(advert["location"]["region"]["name"]),
                "bump_up": params.get("bump_up"),
                "export_olx": params.get("export_olx"),
                "priceevaluation": advert["priceEvaluation"]["indicator"],
                "cepikVerified": advert["cepikVerified"],
            }
        )

    return listings


def parse_graphql(html: str) -> list[dict]:

    # find json from "Props" script
    next_data = json.loads(find_props_script(html))
    # extract urqlState json
    urql_state = extract_urql_state(next_data)
    # locate listings data id
    advert_search_state = find_advert_search_state(urql_state)
    # decode json
    graphql_json = decode_graphql_data(advert_search_state)
    # output listings into a list of dicts
    results = extract_listings_from_graphql(graphql_json)

    return results


if __name__ == "__main__":

    html_file_path = os.path.join(
        os.path.dirname(__file__),
        "../../data/html_snapshots/volkswagen_taigo_page_1.html",
    ).replace("\\", "/")

    with open(html_file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    listings = parse_graphql(html_content)

    for i in range(len(listings)):
        print(listings[i])

    # import pandas as pd

    # df = pd.DataFrame(listings)
    # df.to_csv("output.csv", index=False)
