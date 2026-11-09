import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="PropCompare UAE", page_icon="🏙️", layout="wide")

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "sample_listings.csv"

st.markdown("""
<style>
.main {background-color: #f7f9fc;}
.block-container {padding-top: 1.6rem; padding-bottom: 2rem;}
.hero {padding: 1.5rem 1.8rem; border-radius: 16px; background: linear-gradient(115deg,#102a43,#176b87); color: white; margin-bottom: 1rem;}
.hero h1 {color:white; margin-bottom:0.2rem;}
.hero p {color:#e5f2f7; margin-bottom:0;}
.small-note {color:#667085; font-size:0.85rem;}
.listing {border:1px solid #e5eaf0; border-radius:12px; padding:14px; background:white; margin-bottom:8px;}
</style>
""", unsafe_allow_html=True)

def load_data():
    df = pd.read_csv(DATA_PATH)
    return df

def score_listing(row, budget_max, preferred_emirate, preferred_type, min_beds):
    # Transparent, illustrative weighted score (not an investment valuation).
    score = 0
    if budget_max > 0:
        score += max(0, 1 - max(0, row["price_aed"] - budget_max) / budget_max) * 35
    if preferred_emirate == "Any" or row["emirate"] == preferred_emirate:
        score += 25
    if preferred_type == "Any" or row["property_type"] == preferred_type:
        score += 20
    if row["bedrooms"] >= min_beds:
        score += 10
    score += min(row["area_sqft"] / 3000, 1) * 10
    return round(min(score, 100), 1)

df = load_data()

st.markdown("""
<div class="hero">
  <h1>🏙️ PropCompare UAE</h1>
  <p>Compare property listings across the UAE. Filter by your needs, understand value, and shortlist with confidence.</p>
</div>
""", unsafe_allow_html=True)

st.caption("Academic prototype • Demo listings are illustrative and are not live market offers.")
with st.sidebar:
    st.header("🔎 Find your property")
    purpose = st.selectbox("Looking to", ["For Sale", "For Rent"])
    emirates = ["Any"] + sorted(df["emirate"].dropna().unique().tolist())
    emirate = st.selectbox("Emirate", emirates)
    location_options = ["Any"] + sorted(df.loc[df["emirate"].eq(emirate), "location"].dropna().unique().tolist()) if emirate != "Any" else ["Any"] + sorted(df["location"].dropna().unique().tolist())
    location = st.selectbox("Area / neighbourhood", location_options)
    prop_types = ["Any"] + sorted(df["property_type"].dropna().unique().tolist())
    prop_type = st.selectbox("Property type", prop_types)
    budget_min, budget_max = st.slider("Budget (AED)", 0, 5_000_000, (0, 2_500_000), step=50_000, format="AED %d")
    bedrooms = st.selectbox("Minimum bedrooms", [0, 1, 2, 3, 4, 5], index=0, format_func=lambda x: "Any" if x == 0 else f"{x}+")
    min_area = st.number_input("Minimum area (sq. ft.)", min_value=0, max_value=10000, value=0, step=50)
    status_filter = st.selectbox("Property status", ["Any", "Ready", "Off-plan"])
    furnishing = st.selectbox("Furnishing", ["Any", "Furnished", "Unfurnished"])
    st.divider()
    st.caption("You can also upload your own CSV dataset below.")

uploaded = st.file_uploader("Upload property listings CSV (optional)", type=["csv"])
if uploaded is not None:
    try:
        user_df = pd.read_csv(uploaded)
        required = set(df.columns)
        if required.issubset(user_df.columns):
            df = user_df.copy()
            st.success(f"Loaded {len(df)} rows from your CSV.")
        else:
            st.error("CSV is missing required columns. Download/check data/sample_listings.csv for the expected format.")
    except Exception as e:
        st.error(f"Could not read CSV: {e}")

# Ensure numeric fields are usable.
for col in ["price_aed", "bedrooms", "bathrooms", "area_sqft"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.dropna(subset=["price_aed", "area_sqft", "bedrooms"])

filtered = df[df["purpose"].eq(purpose)].copy()
if emirate != "Any": filtered = filtered[filtered["emirate"].eq(emirate)]
if location != "Any": filtered = filtered[filtered["location"].eq(location)]
if prop_type != "Any": filtered = filtered[filtered["property_type"].eq(prop_type)]
filtered = filtered[filtered["price_aed"].between(budget_min, budget_max)]
if bedrooms > 0: filtered = filtered[filtered["bedrooms"] >= bedrooms]
filtered = filtered[filtered["area_sqft"] >= min_area]
if status_filter != "Any": filtered = filtered[filtered["status"].eq(status_filter)]
if furnishing != "Any": filtered = filtered[filtered["furnishing"].eq(furnishing)]

if not filtered.empty:
    filtered["price_per_sqft"] = filtered["price_aed"] / filtered["area_sqft"]
    filtered["match_score"] = filtered.apply(lambda r: score_listing(r, budget_max, emirate, prop_type, bedrooms), axis=1)
    filtered = filtered.sort_values(["match_score", "price_per_sqft"], ascending=[False, True])

k1, k2, k3, k4 = st.columns(4)
k1.metric("Matching properties", f"{len(filtered):,}")
k2.metric("Lowest listed price", f"AED {filtered['price_aed'].min():,.0f}" if len(filtered) else "—")
k3.metric("Average price", f"AED {filtered['price_aed'].mean():,.0f}" if len(filtered) else "—")
k4.metric("Average price / sq. ft.", f"AED {filtered['price_per_sqft'].mean():,.0f}" if len(filtered) else "—")
st.divider()

tab1, tab2, tab3 = st.tabs(["🏡 Property results", "⚖️ Compare properties", "📊 Market insights"])

with tab1:
    st.subheader("Best matches for your filters")
    if filtered.empty:
        st.info("No properties match these filters. Try increasing your budget or widening the location.")
    else:
        st.caption("Ranked using the prototype match score. Scores are preference-fit indicators, not professional valuations.")
        for _, r in filtered.iterrows():
            with st.container(border=True):
                a, b, c = st.columns([4, 1.3, 1.3])
                with a:
                    st.markdown(f"**{r['title']}** · {r['property_type']}")
                    st.write(f"📍 {r['location']}, {r['emirate']}  ·  {int(r['bedrooms'])} bed  ·  {int(r['bathrooms'])} bath  ·  {r['area_sqft']:,.0f} sq. ft.")
                    st.caption(f"{r['status']} · {r['furnishing']} · Source: {r['source']}")
                with b:
                    st.metric("Price", f"AED {r['price_aed']:,.0f}")
                    st.caption(f"AED {r['price_per_sqft']:,.0f} / sq. ft.")
                with c:
                    st.metric("Match score", f"{r['match_score']:.0f}/100")
                    st.link_button("Open source", str(r["source_url"]), use_container_width=True)

with tab2:
    st.subheader("Side-by-side comparison")
    if filtered.empty:
        st.info("No results to compare yet.")
    else:
        options = filtered["listing_id"].astype(str).tolist()
        selected = st.multiselect("Choose up to 4 properties", options, default=options[:min(2, len(options))], max_selections=4,
                                  format_func=lambda x: f"{x} — {filtered.loc[filtered['listing_id'].astype(str).eq(x), 'title'].iloc[0]}")
        comp = filtered[filtered["listing_id"].astype(str).isin(selected)].copy()
        if not comp.empty:
            view = comp[["title","emirate","location","property_type","price_aed","bedrooms","bathrooms","area_sqft","price_per_sqft","status","match_score"]].T
            view.columns = comp["listing_id"].astype(str)
            st.dataframe(view, use_container_width=True)
            chart = px.bar(comp, x="title", y="price_aed", color="emirate", title="Asking price comparison", labels={"price_aed":"Price (AED)", "title":"Property"})
            st.plotly_chart(chart, use_container_width=True)

with tab3:
    st.subheader("Insights from the filtered listings")
    if filtered.empty:
        st.info("Apply broader filters to see insights.")
    else:
        left, right = st.columns(2)
        with left:
            p = px.bar(filtered.groupby("emirate", as_index=False)["price_aed"].mean(), x="emirate", y="price_aed",
                       title="Average asking price by emirate", labels={"price_aed":"Average price (AED)"})
            st.plotly_chart(p, use_container_width=True)
        with right:
            q = px.scatter(filtered, x="area_sqft", y="price_aed", color="property_type", hover_name="title",
                           title="Price vs. property size", labels={"area_sqft":"Area (sq. ft.)", "price_aed":"Price (AED)"})
            st.plotly_chart(q, use_container_width=True)
        st.download_button("⬇️ Download filtered results (CSV)", filtered.to_csv(index=False).encode("utf-8"),
                           file_name="propcompare_filtered_results.csv", mime="text/csv")

st.divider()
with st.expander("ℹ️ Data, limitations & methodology"):
    st.markdown("""
    **Important:** This starter project ships with illustrative sample records so the app works immediately for a classroom demonstration. It does not crawl the entire internet and the sample listings are not verified live offers.

    **Real data integration:** connect approved APIs, licensed property feeds, or partner exports from portals/agents. Respect each provider's terms, robots rules, rate limits, attribution and display requirements. Do not scrape sites where access is prohibited.

    **Prototype ranking:** match score combines budget fit (35%), emirate fit (25%), property-type fit (20%), bedroom fit (10%) and floor-area preference (10%). The weights are transparent and can be adjusted. A high score is not investment, legal, or valuation advice.

    **Suggested production improvements:** verified listing timestamps, duplicate detection, currency/unit validation, source freshness labels, price history, map view, and a secure backend database.
    """)
st.caption("PropCompare UAE · Student demonstration project")
