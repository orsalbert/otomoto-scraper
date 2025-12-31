## 🚗 Otomoto Used Car Market Analyzer

A data-driven toolchain to **scrape, analyze, and evaluate used car listings from Otomoto.pl**, with the goal of identifying **fair prices, undervalued deals, and negotiation opportunities**.

This project combines:

* Web scraping (BeautifulSoup + requests)
* Structured data extraction (JSON-LD + embedded GraphQL)
* Data normalization & deduplication
* Exploratory data analysis in Jupyter
* Price trend tracking
* A lightweight HTML UI to configure and run scrapes

## 🎯 Project Goals

The primary goal is **better buying decisions**.

Specifically, the project aims to:

* Build a **clean, structured dataset** of comparable used car listings
* Normalize key attributes (engine, trim, mileage, seller type)
* Track **price evolution over time**
* Identify:
  * Undervalued listings
  * Overpriced / “stuck” inventory
  * Seller behavior patterns
* Provide **visual, interpretable insights** via a Jupyter notebook
* Allow users to **configure search parameters** via a simple HTML interface

## 🧠 Key Questions This Project Answers

* What is a *fair market price* for a given car configuration?
* How much does mileage really affect price?
* Are imports priced differently than domestic cars?
* Do dealers drop prices faster than private sellers?
* Which listings are likely negotiable?
* Which trims / engines offer the best value for money?

## 🔍 Data Sources & Extraction Strategy

The scraper extracts listings from **two independent structured sources** embedded in Otomoto pages:

### 1️⃣ JSON-LD (`application/ld+json`)

* Provides:
  * Title
  * Brand & model
  * Fuel type
  * Mileage
  * Price
* Stable but limited

### 2️⃣ Embedded GraphQL (Next.js + URQL state)

* Provides:
  * Internal advert ID
  * Upload date
  * Short description
  * Advert URL
  * Seller info
  * Full parameters (engine, trim, gearbox, origin, year)
  * Location
  * Price evaluation badges
  * CEPiK verification
* Extracted via **double-decoded JSON**

The two sources are merged.

## 🧮 Feature Engineering & Calculated Columns

The analysis layer adds derived metrics such as:

* `price_per_1k_km`
* `days_on_market`
* `price_percentile`
* `is_dealer`
* Normalized engine & trim identifiers
* Price deltas over time (for repeated scrapes)

These features enable  **market-relative comparisons** , not just raw price sorting.

## 📊 Analysis & Visualization (Jupyter)

The notebooks focus on  **decision-oriented insights** , including:

* Price vs mileage scatter plots
* Boxplots by engine power, trim, origin
* Distribution of days on market
* Identification of undervalued & overpriced listings
* Seller behavior patterns
* Time-based price trends

The final notebook acts as a **lightweight analytical dashboard**.	

## 🖥 HTML UI (Scraper Configuration)

A simple HTML page allows the user to:

* Select:
  * Brand & model
  * Year range
  * Price range
  * Mileage limit
  * Fuel type
  * Gearbox
  * Accident indicator
* Trigger the scraper locally
* Generate updated CSV

This is intentionally lightweight — the UI is a **parameter input layer**.

## ⚙️ Requirements

### Python version

```
Python 3.10+
```

### Core dependencies

```
requests
beautifulsoup4
pandas
numpy
matplotlib
jupyter
pyarrow        # for Parquet support
```

Optional (future extensions):

```
scikit-learn   # price modeling
plotly         # interactive dashboards
```

## 🚀 How to Run

```bash
pip install -r requirements.txt
python run_scraper.py
```

Then open:

```bash
jupyter notebook
```

and explore the notebooks in `notebooks/`.

## ⚠️ Disclaimer

This project is for **educational and personal research purposes**.
Always respect the target website’s terms of service and use reasonable rate limiting.

## 🧭 Roadmap / Future Ideas

* Automated fair-price model
* Alerting for new undervalued listings
* Negotiation score per listing
* Multi-model comparison (Taigo vs Kamiq vs Kadjar)
