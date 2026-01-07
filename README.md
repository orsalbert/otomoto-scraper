## Hi, otomoto’s calling: Let’s scrape!

This project is a practical, end-to-end data engineering and analysis workflow built around one real-world problem:  **how to make better, data-driven decisions when buying a used car**.

It combines a lightweight frontend, a Python backend, web scraping, data normalization, and analytical notebooks into a single, coherent pipeline. The goal is not just to extract data, but to **build a usable dataset, transform it into insight, and act on it**.

Web scraping, backend development, data processing, and exploratory analysis — all in one place!

---

## Project goals

The main objectives of this project are:

* Build a **repeatable dataset** of used car listings based on user-defined criteria
* Normalize and enrich raw scraped data into analysis-ready tables
* Apply analytical logic to rank, filter, and evaluate listings
* Support a structured **buyer’s funnel** from broad market scan to a final purchase shortlist
* Keep the system simple, inspectable, and easy to extend

The project intentionally avoids over-engineering and instead focuses on clarity, correctness, and real decision support.

---

## High-level workflow

1. User selects car models and search parameters via a lightweight web UI
2. Parameters are saved as a JSON configuration through a Flask backend
3. The scraper runs using the provided configuration and saves a raw CSV snapshot
4. A normalization step cleans, standardizes, and enriches the dataset
5. Analysis is performed in Jupyter notebooks to guide buying decisions

Each step produces explicit, versionable outputs to make debugging and iteration easy.

---

## Frontend

The frontend is intentionally minimal and static.

* HTML for structure
* CSS for basic layout
* JavaScript for form handling and submission

Its role is not to be a full web application, but a **parameter selection interface** that allows non-technical input into the scraping pipeline.

---

## Backend

The backend is written in Python and built around Flask.

Responsibilities include:

* Receiving user input from the frontend
* Persisting scraping configurations as JSON
* Triggering scraping runs
* Coordinating data output to disk

The backend is designed to be transparent and observable, with all artifacts saved locally for inspection.

---

## Data processing and normalization

Raw scraped listings are not immediately suitable for analysis. A dedicated normalization step:

* Cleans inconsistent fields
* Standardizes naming and categories
* Adds calculated convenience columns
* Enriches geographic and technical attributes

The output is a processed CSV intended to be directly loaded into analytical notebooks.

---

## Analysis and buyer’s funnel

All analysis lives in  **Jupyter notebooks** .

The analytical workflow follows a buyer’s funnel approach:

1. **Market overview**
   Understand price ranges, mileage distributions, and model availability.
2. **Filtering and constraints**
   Apply geographic, technical, and trust-based filters (e.g. region, verification flags).
3. **Value signals**
   Use derived metrics such as price per kilometer, price per horsepower, and age-adjusted pricing.
4. **Shortlisting**
   Narrow the dataset to a small number of high-value candidates.
5. **Decision support**
   Explicit buy/no-buy flags, notes, and follow-up actions.

The notebooks are designed to support  **human judgment** , not replace it.

---

## Requirements

Python 3.10+

Core libraries:

* requests
* beautifulsoup4
* lxml
* pandas
* tqdm
* flask
* flask-cors

Analysis:

* jupyter
* numpy
* matplotlib
* seaborn

Install dependencies with:

```
pip install -r requirements.txt
```

---

## Disclaimer

This project is intended for **educational and personal research purposes only**.

* It is not affiliated with otomoto or any related service
* Scraping should always respect website terms of service
* Use responsibly and ethically

The author takes no responsibility for misuse or violations of third-party policies.

---

## Closing note

This project started as a personal need — choosing the right car — and evolved into a complete data pipeline. It reflects a way to approach problems: start with a real question, build the tools to answer it, and iterate until the data tells a story.
