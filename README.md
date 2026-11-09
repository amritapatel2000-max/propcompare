# PropCompare UAE

A simple Streamlit prototype for comparing UAE property listings by price, location, type, size and other preferences.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository and upload the contents of this ZIP.
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Select the repository, branch (`main`) and main file path (`app.py`).
4. Deploy. Streamlit installs packages from `requirements.txt`.

## Dataset
`data/sample_listings.csv` is illustrative demo data. It is included so the app can be demonstrated immediately. Replace it with data you have permission to use, or upload a CSV in the app.

Required CSV columns:
`listing_id, property_type, emirate, location, title, purpose, price_aed, bedrooms, bathrooms, area_sqft, status, furnishing, source, source_url`

Purpose values: `For Sale` or `For Rent`.
Status values: `Ready` or `Off-plan`.

## Important data limitation
No single public feed guarantees every property listing on the internet across the UAE. A real deployment needs permitted APIs, licensed feeds or partner exports, plus source attribution and refresh processes. The app does not scrape property portals. The included sample listings are not live offers.

## Project structure
```
propcompare_uae/
├── app.py
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
└── data/
    └── sample_listings.csv
```
