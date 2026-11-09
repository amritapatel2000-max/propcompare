# PropCompare UAE — Architecture & User Flow

## Goal
A student-friendly property comparison platform for UAE listings. Users filter listings and compare shortlist candidates using transparent metrics.

## High-level architecture
1. **Source layer** — licensed portal APIs, agent/partner feeds, or user-uploaded CSV exports.
2. **Ingestion layer** — scheduled import, schema validation, currency/unit normalisation, source timestamps.
3. **Data quality layer** — duplicate detection, missing-field checks, stale-listing flags.
4. **Storage layer** — CSV for this prototype; PostgreSQL/Supabase can replace it for a larger project.
5. **Business logic** — filtering, price-per-square-foot calculation, weighted preference match score.
6. **Presentation layer** — Streamlit pages/tabs for search, results, comparison and insights.

## User flow
Home → choose Buy/Rent → select emirate/area → set budget and property requirements → view matching results → sort/rank → compare up to four properties → open original source / export shortlist.

## Ranking model (prototype)
- Budget fit: 35 points
- Emirate fit: 25 points
- Property type fit: 20 points
- Bedroom fit: 10 points
- Floor-area preference: 10 points

Total is capped at 100. This is a preference-fit score, not an investment recommendation or valuation.

## Core data fields
Listing ID, title, property type, emirate, neighbourhood, sale/rent, asking price (AED), bedrooms, bathrooms, area (sq. ft.), ready/off-plan, furnishing, source name, source URL.

## Production considerations
- Obtain explicit data permissions and follow provider terms.
- Show provider, original listing link, last-updated timestamp and data freshness.
- Deduplicate listings across sources and flag unavailable/removed listings.
- Validate sale/rent periods and AED amounts; rental prices may be annual, quarterly or monthly and must be labelled consistently.
- Add maps, saved searches, user accounts and a database only if the project scope expands.
