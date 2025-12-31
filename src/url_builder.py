from urllib.parse import urlencode


BRAND_MODEL_SLUGS = {
    ("volkswagen", "taigo"): ("volkswagen", "taigo"),
    ("renault", "kadjar"): ("renault", "kadjar"),
    ("skoda", "kamiq"): ("skoda", "kamiq"),
    ("seat", "ateca"): ("seat", "ateca"),
    ("ford", "puma"): ("ford", "puma"),
    ("ford", "kuga"): ("ford", "kuga"),
    ("suzuki", "sx4-s-cross"): ("suzuki", "sx4-s-cross"),
    ("honda", "hr-v"): ("honda", "hr-v"),
}


def build_query_params(
    price_from: int,
    price_to: int,
    year_to: int,
    mileage_to: int,
    fuel_type: str,
    gearbox: str,
    accident_free: bool,
    page: int | None = None,
):
    params = {
        "search[filter_float_price:from]": price_from,
        "search[filter_float_price:to]": price_to,
        "search[filter_float_year:to]": year_to,
        "search[filter_float_mileage:to]": mileage_to,
        "search[filter_enum_fuel_type]": fuel_type,
        "search[filter_enum_gearbox]": gearbox,
    }

    if accident_free:
        params["search[filter_enum_damaged]"] = 0

    if page is not None:
        params["page"] = page

    return urlencode(params, doseq=True)


def build_search_url(
    brand: str,
    model: str,
    year_from: int,
    price_from: int,
    price_to: int,
    year_to: int,
    mileage_to: int,
    fuel_type: str = "petrol",
    gearbox: str = "manual",
    accident_free: bool = True,
    page: int | None = None,
):
    key = (brand.lower(), model.lower())
    if key not in BRAND_MODEL_SLUGS:
        raise ValueError(f"Unsupported brand/model: {brand} {model}")

    brand_slug, model_slug = BRAND_MODEL_SLUGS[key]

    base_url = (
        f"https://www.otomoto.pl/osobowe/" f"{brand_slug}/{model_slug}/od-{year_from}"
    )

    query_string = build_query_params(
        price_from=price_from,
        price_to=price_to,
        year_to=year_to,
        mileage_to=mileage_to,
        fuel_type=fuel_type,
        gearbox=gearbox,
        accident_free=accident_free,
        page=page,
    )

    return f"{base_url}?{query_string}"


# if __name__ == "__main__":
#     url = build_search_url(
#         brand="Volkswagen",
#         model="Taigo",
#         year_from=2019,
#         price_from=50000,
#         price_to=75000,
#         year_to=2022,
#         mileage_to=150000,
#         fuel_type="petrol",
#         gearbox="manual",
#         accident_free=True,
#         page=1,
#     )

#     print(url)


def generate_paginated_urls(base_args: dict, max_pages: int = 5):
    urls = []
    for page in range(1, max_pages + 1):
        url = build_search_url(page=page, **base_args)
        urls.append(url)
    return urls


# base_args = {
#     "brand": "Volkswagen",
#     "model": "Taigo",
#     "year_from": 2019,
#     "price_from": 50000,
#     "price_to": 75000,
#     "year_to": 2022,
#     "mileage_to": 150000,
# }

# urls = generate_paginated_urls(base_args, max_pages=3)
# for u in urls:
#     print(u)
