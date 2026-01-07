import re
from typing import Dict, Any
import pandas as pd
from get_eur import fetch_rate
from datetime import datetime

# =========================
# CONFIG
# =========================

zone_code = {
    "zachodniopomorskie": "N",
    "pomorskie": "N",
    "warminsko-mazurskie": "N",
    "kujawsko-pomorskie": "N",
    "podlaskie": "N",
    "lubuskie": "C",
    "wielkopolskie": "C",
    "lodzkie": "C",
    "mazowieckie": "C",
    "lubelskie": "C",
    "dolnoslaskie": "S",
    "opolskie": "S",
    "slaskie": "S",
    "swietokrzyskie": "S",
    "malopolskie": "S",
    "podkarpackie": "S",
}

# =========================
# HELPERS
# =========================


def safe_int(val):
    try:
        return int(val)
    except Exception:
        return None


def parse_version_slug(version: str) -> Dict[str, Any]:
    if not isinstance(version, str) or not version.startswith("ver-"):
        return {
            "engine_size_l": None,
            "engine_family": None,
            "drivetrain": None,
            "trim": None,
            "feature_flags": None,
        }

    v = version.replace("ver-", "").lower()
    parts = v.split("-")

    # Try to find engine size as a float (e.g., 1.3, 1.5, 2.0)
    engine_size = None
    for i, p in enumerate(parts):
        if re.match(r"^\d+(?:\.\d+)?$", p):
            try:
                size = float(p)
                if size <= 2.0:  # Only accept reasonable engine sizes
                    # But check if next part is also a number (e.g., 1.3 → 1 and 3)
                    if i + 1 < len(parts) and re.match(
                        r"^\d+(?:\.\d+)?$", parts[i + 1]
                    ):
                        # Check if it's a decimal-like pair (e.g., 1.3)
                        next_p = parts[i + 1]
                        if re.match(r"^\d+(?:\.\d+)?$", next_p):
                            # Try to combine: 1.3 → 1.3
                            combined = f"{p}.{next_p}"
                            try:
                                combined_size = float(combined)
                                if combined_size <= 2.0:
                                    engine_size = combined_size
                                    break
                            except:
                                pass
                    else:
                        # Single number like 1.0, 1.5
                        engine_size = size
                        break
            except:
                pass

    # Known engine families
    engine_families = [
        "tsi",
        "tce",
        "ecoboost",
        "mhev",
        "hybrid",
        "boosterjet",
        "energy",
        "t",
        "eco-tsi",
    ]
    engine_family = None
    for p in parts:
        if p in engine_families:
            engine_family = p
            break

    # Drivetrain mapping
    drivetrain_map = {
        "fwd": "FWD",
        "awd": "AWD",
        "4wd": "4WD",
        "2x4": "FWD",
        "allgrip": "AWD",
    }
    drivetrain = None
    for p in parts:
        if p in drivetrain_map:
            drivetrain = drivetrain_map[p]
            break

    # Trim: last non-numeric, non-family, non-drivetrain word
    trim = None
    for p in reversed(parts):
        if (
            p not in engine_families
            and p not in drivetrain_map
            and not re.match(r"^\d+(?:\.\d+)?$", p)
        ):
            trim = p.title()
            break

    # Features: everything else
    features = []
    for p in parts:
        if p not in [str(engine_size), engine_family, drivetrain] and not re.match(
            r"^\d+(?:\.\d+)?$", p
        ):
            features.append(p)

    return {
        "engine_size_l": engine_size,
        "engine_family": engine_family,
        "drivetrain": drivetrain,
        "trim": trim,
        "feature_flags": ",".join(features) if features else None,
    }


# =========================
# MAIN NORMALIZER
# =========================


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    # ---- renaming ----
    df = df.rename(columns={"price": "price_pln"})

    # ---- typing ----
    numeric_cols = [
        "id",
        "price_pln",
        "mileage",
        "year",
        "engine_capacity",
        "engine_power",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    bool_cols = ["cepikVerified"]
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype("boolean")

    # ---- casing ----
    text_cols = [
        "brand",
        "model",
        "fuel_type",
        "gearbox",
        "country_origin",
        "city",
        "region",
        "seller_site",
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].str.lower()

    # ---- date added and days passed ----
    df["date_added"] = pd.to_datetime(df["date_added"])
    df["current_date"] = pd.Timestamp.now(tz="Europe/Warsaw")
    df["days_listed"] = (df["current_date"] - df["date_added"]).dt.days

    # ---- zone code ----
    df["zone_code"] = df["region"].map(zone_code).fillna("UNK")

    # ---- currency conversion ----
    date, eur_rate = fetch_rate()
    print(f"Latest PLN to EUR exchange rate on {date} is {eur_rate}")

    df["pln_eur_rate"] = eur_rate
    df["price_eur"] = (df["price_pln"] / eur_rate).round(0)

    # ---- version parsing ----
    parsed_versions = df["version"].apply(parse_version_slug).apply(pd.Series)
    df = pd.concat([df, parsed_versions], axis=1)

    # ---- convenience columns ----
    df["price_per_km"] = (df["price_pln"] / df["mileage"]).round(2)
    df["price_per_hp"] = (df["price_pln"] / df["engine_power"]).round(0)
    df["scrape_year"] = datetime.now().year
    df["car_age"] = df["scrape_year"] - df["year"]
    df["price_per_year"] = (df["price_pln"] / df["car_age"]).round(0)

    df["value_index"] = (
        (df["price_per_km"] * 0.4)
        + (df["price_per_hp"] * 0.3)
        + (df["price_per_year"] * 0.3)
    ).round(0)

    # Market deviation proxy
    df["price_per_hp_bucket"] = pd.qcut(
        df["price_per_hp"], 5, labels=["very_low", "low", "avg", "high", "very_high"]
    )

    # Power density - detects modern turbo vs older naturally aspirated
    df["hp_per_liter"] = (df["engine_power"] / (df["engine_capacity"] / 1000)).round(1)

    # Shows how intensively the car was used annually
    df["km_per_year"] = (df["mileage"] / df["car_age"]).round(0)

    df["price_bucket"] = pd.cut(
        df["price_pln"],
        bins=[0, 55000, 65000, 75000, 90000],
        labels=["low", "mid", "high", "premium"],
    )

    df["mileage_bucket"] = pd.cut(
        df["mileage"],
        bins=[0, 30000, 60000, 100000, 150000, 250000],
        labels=["very_low", "low", "mid", "high", "very_high"],
    )

    df["polish_origin"] = df["country_origin"].str.contains("pol", case=False, na=False)

    df["is_dealer"] = df["seller_name"].notna()

    df["risk_score"] = (
        (~df["cepikVerified"]).astype(int) * 2
        + (df["polish_origin"] == False).astype(int)
        + (df["mileage"] > 130000).astype(int)
    )

    big_cities = [
        "warszawa",
        "krakow",
        "wroclaw",
        "gdansk",
        "poznan",
        "lodz",
        "szczecin",
        "bydgoszcz",
        "lublin",
        "bialystok",
        "katowice",
        "czestochowa",
        "radom",
        "sosnowiec",
        "torun",
        "kielce",
        "gliwice",
        "tarnow",
    ]

    df["big_city"] = df["city"].str.lower().isin(big_cities)

    df["region_price_density"] = df.groupby("region")["price_pln"].transform("median")

    # # ---- ordering ----
    preferred_order = [
        "id",
        "date_added",
        "current_date",
        "days_listed",
        "title",
        "brand",
        "model",
        "version",
        "year",
        "mileage",
        "price_pln",
        "price_eur",
        "pln_eur_rate",
        "engine_capacity",
        "engine_power",
        "engine_family",
        "engine_size_l",
        "drivetrain",
        "trim",
        "feature_flags",
        "gearbox",
        "fuel_type",
        "country_code",
        "country_origin",
        "city",
        "big_city",
        "region",
        "zone_code",
        "region_price_density",
        "seller_name",
        "seller_site",
        "short_description",
        "bump_up",
        "export_olx",
        "priceevaluation",
        "cepikVerified",
        "price_per_km",
        "price_per_hp",
        "scrape_year",
        "car_age",
        "price_per_year",
        "value_index",
        "price_per_hp_bucket",
        "hp_per_liter",
        "km_per_year",
        "price_bucket",
        "mileage_bucket",
        "polish_origin",
        "is_dealer",
        "risk_score",
        "url",
    ]

    return df[preferred_order]


if __name__ == "__main__":
    from pathlib import Path

    # Example usage
    project_root = Path.cwd().parent
    df = pd.read_csv(project_root / "data/raw_csv/raw_listings_20260102.csv")

    df_normalized = normalize_dataframe(df)

    # Save normalized data
    df_normalized.to_csv(
        project_root / "data/processed_csv/normalized.csv", index=False
    )
    print("Normalized data saved!")
