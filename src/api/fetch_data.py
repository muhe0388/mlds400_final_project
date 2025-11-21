# src/api/fetch_data.py

import os
import time
import pandas as pd
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

# Resolve absolute path to project root so data always goes to repo/data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


##############################################################################
# 1) Fetch business-level restaurant data (local_results) for ONE center
##############################################################################
def fetch_places(query="restaurants",
                 ll="@41.8781,-87.6298,14z",
                 max_pages=3,
                 page_sleep=1.2):
    """
    Fetch restaurant-level results from Google Maps via SerpApi
    for a single center (ll). Supports pagination via 'start'.
    Returns a DataFrame of unique restaurants.
    """
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise RuntimeError("Missing SERPAPI_KEY in .env")

    all_rows = []

    for page in range(max_pages):
        start = page * 20  # Google Maps typically returns ~20 results per page
        params = {
            "engine": "google_maps",
            "q": query,
            "ll": ll,              # latitude/longitude/zoom
            "type": "search",
            "start": start,        # pagination offset
            "api_key": api_key,
        }

        print(f"\n[fetch_places] Fetching page {page + 1} (start={start}) for ll={ll} ...")
        results = GoogleSearch(params).get_dict()
        rows = results.get("local_results", []) or []
        print(f"[fetch_places] Retrieved {len(rows)} rows")

        all_rows.extend(rows)

        # If fewer than 20 results, likely reached the last page
        if len(rows) < 20:
            break

        time.sleep(page_sleep)

    df_places = pd.DataFrame(all_rows)
    if not df_places.empty:
        df_places = df_places.drop_duplicates(subset=["data_id"])

    return df_places


##############################################################################
# 2) Fetch reviewer-level data for each restaurant using its data_id
##############################################################################
def fetch_reviews(df_places,
                  max_places=20,
                  max_reviews_per_place=20,
                  sleep_between=1.0):
    """
    Fetch reviewer-level data using the 'google_maps_reviews' engine.
    Each restaurant is identified by its data_id.
    Produces raw_reviews.csv containing review text, rating, user info, etc.
    """
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise RuntimeError("Missing SERPAPI_KEY in .env")

    review_rows = []

    # Limit number of restaurants to avoid exhausting API credits
    subset = df_places.head(max_places)

    for idx, row in subset.iterrows():
        data_id = row.get("data_id")
        title = row.get("title")

        if not data_id:
            continue

        print(f"\n[fetch_reviews] {idx + 1}/{len(subset)}: {title}")

        params = {
            "engine": "google_maps_reviews",
            "data_id": data_id,
            "hl": "en",
            "api_key": api_key,
        }

        results = GoogleSearch(params).get_dict()
        reviews = results.get("reviews", []) or []
        print(f"[fetch_reviews] Retrieved {len(reviews)} reviews")

        # Limit the number of reviews per restaurant
        for r in reviews[:max_reviews_per_place]:
            review_rows.append({
                # Restaurant (business-level) info
                "place_data_id": data_id,
                "place_title": title,
                "place_rating": row.get("rating"),
                "place_reviews_count": row.get("reviews"),
                "place_price": row.get("price"),
                "place_type": row.get("type"),

                # Reviewer-level info
                "review_user": r.get("user"),
                "review_rating": r.get("rating"),
                "review_text": r.get("snippet") or r.get("text"),
                "review_date": r.get("date"),
                "review_likes": r.get("likes"),
            })

        time.sleep(sleep_between)

    df_reviews = pd.DataFrame(review_rows)
    out_path = os.path.join(DATA_DIR, "raw_reviews.csv")
    df_reviews.to_csv(out_path, index=False)

    print(f"\n[fetch_reviews] Saved {len(df_reviews)} reviews → {out_path}")
    return df_reviews


##############################################################################
# 3) Generic: fetch restaurants for ONE center + optional reviews
##############################################################################
def fetch_all(query="restaurants",
              ll="@41.8781,-87.6298,14z",
              max_pages=3,
              fetch_review_data=True):
    """
    Run the full pipeline for a single center:
    1) Fetch restaurant-level results.
    2) (Optional) Fetch reviewer-level data.
    Saves restaurants to raw_restaurants.csv and reviews to raw_reviews.csv.
    """
    df_places = fetch_places(query, ll, max_pages)

    # Save restaurants
    out_path = os.path.join(DATA_DIR, "raw_restaurants.csv")
    df_places.to_csv(out_path, index=False)
    print(f"\n[fetch_all] Saved {len(df_places)} unique restaurants → {out_path}")

    df_reviews = None
    if fetch_review_data and not df_places.empty:
        df_reviews = fetch_reviews(df_places)

    return df_places, df_reviews


##############################################################################
# 4) Evanston-specific helper: use multiple centers & merge
##############################################################################
def fetch_evanston_multi_center(fetch_review_data=True,
                                max_pages_per_center=2):
    """
    Fetch Evanston restaurant data using multiple centers
    (North, Downtown, South Evanston), then merge & de-duplicate.
    Optionally fetch reviewer-level data on top of that.

    Final restaurant output is saved to data/raw_restaurants.csv
    (Evanston-focused dataset).
    """
    centers = [
        "@42.0646,-87.6904,14z",  # North Evanston / Central St
        "@42.0451,-87.6880,14z",  # Downtown Evanston
        "@42.0333,-87.6811,14z",  # South Evanston / Main St
    ]

    dfs = []
    for ll in centers:
        print(f"\n[fetch_evanston_multi_center] Fetching for center: {ll}")
        df_center = fetch_places(
            query="restaurants",
            ll=ll,
            max_pages=max_pages_per_center,
            page_sleep=1.2,
        )
        dfs.append(df_center)

    if dfs:
        df_places = pd.concat(dfs, ignore_index=True)
        df_places = df_places.drop_duplicates(subset=["data_id"])
    else:
        df_places = pd.DataFrame()

    # Save merged Evanston restaurants
    out_path = os.path.join(DATA_DIR, "raw_restaurants.csv")
    df_places.to_csv(out_path, index=False)
    print(f"\n[fetch_evanston_multi_center] Saved {len(df_places)} unique Evanston restaurants → {out_path}")

    df_reviews = None
    if fetch_review_data and not df_places.empty:
        df_reviews = fetch_reviews(df_places)

    return df_places, df_reviews


##############################################################################
# Entry point: run Evanston multi-center by default
##############################################################################
if __name__ == "__main__":
    # This will fetch Evanston restaurants from 3 centers,
    # paginate a bit in each area, merge, deduplicate,
    fetch_evanston_multi_center(
        fetch_review_data=True,   
        max_pages_per_center=2
    )