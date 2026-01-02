import requests
import xml.etree.ElementTree as ET
from pathlib import Path


def fetch_rate():
    """Fetch latest PLN to EUR exchange rate from ECB XML data."""
    # Download the XML file
    url = "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/pln.xml"
    response = requests.get(url)
    response.raise_for_status()  # Raise error if download fails

    # Parse XML
    root = ET.fromstring(response.content)

    # Define namespace (important for XML parsing)
    ns = {"exr": "http://www.ecb.europa.eu/vocabulary/stats/exr/1"}

    # Find all Obs elements and get the last one (latest rate)
    obs_elements = root.findall(".//exr:Obs", ns)

    # Clean up downloaded file
    Path("pln_exchange_rates.xml").unlink(missing_ok=True)

    if obs_elements:
        latest_obs = obs_elements[-1]  # Last element = latest date
        date = latest_obs.get("TIME_PERIOD")
        rate = float(latest_obs.get("OBS_VALUE"))
        return date, rate
    else:
        raise ValueError("No exchange rate data found")


if __name__ == "__main__":
    date, rate = fetch_rate()
    print(f"Latest PLN to EUR exchange rate on {date} is {rate}")
