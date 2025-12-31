import json
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import os


def extract_json_ld(html: str) -> Optional[dict]:
    soup = BeautifulSoup(html, "html.parser")

    script = soup.find(
        "script", {"type": "application/ld+json", "id": "listing-json-ld"}
    )

    if not script or not script.string:
        return None

    try:
        return json.loads(script.string)
    except json.JSONDecodeError:
        return None


def parse_offers(json_ld: dict) -> List[Dict]:
    results = []

    main = json_ld.get("mainEntity", {})
    items = main.get("itemListElement", [])

    for offer in items:
        try:
            price_spec = offer.get("priceSpecification", {})
            item = offer.get("itemOffered", {})

            mileage_obj = item.get("mileageFromOdometer", {})

            results.append(
                {
                    "title": item.get("name"),
                    "brand": item.get("brand"),
                    "fuel_type": item.get("fuelType"),
                    "mileage": (
                        int(mileage_obj.get("value"))
                        if mileage_obj.get("value")
                        else None
                    ),
                    "price": (
                        float(price_spec.get("price"))
                        if price_spec.get("price")
                        else None
                    ),
                    "currency": price_spec.get("priceCurrency"),
                    "source": "json_ld",
                }
            )
        except Exception:
            # never crash parser because of one broken offer
            continue

    return results


def parse_json_ld(html: str) -> List[Dict]:
    json_ld = extract_json_ld(html)

    if not json_ld:
        return []

    return parse_offers(json_ld)


if __name__ == "__main__":
    html_file_path = os.path.join(
        os.path.dirname(__file__),
        "../../data/html_snapshots/volkswagen_taigo_page_1.html",
    ).replace("\\", "/")

    with open(html_file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    print(parse_json_ld(html_content))
