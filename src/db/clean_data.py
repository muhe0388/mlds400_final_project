# src/db/clean_data.py

import pandas as pd
import numpy as np
import sqlite3
import ast
from datetime import datetime, timedelta
import os
import re

"""
clean_data.py
-------------
Reads raw tables, cleans/standardizes fields, parses service options,
converts relative review dates like “1 month ago” into real datetimes,
creates cuisine categories, and writes clean tables back into the DB.
"""

# ============================================================
# Build project paths (safe regardless of where script is run)
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "restaurants.db")





# ============================================================
# Helper: parse dict-like strings (e.g., "{'dine_in': True}")
# ============================================================
def parse_dict(val):
    """Convert a dict-like string into a Python dict. Returns None if parsing fails."""
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        try:
            return ast.literal_eval(val)
        except Exception:
            return None
    return None


def extract_reserve_flag(val):
    """
    Return True if restaurant supports reservations.
    SerpApi uses a URL string for 'reserve_a_table' when available.
    """
    if isinstance(val, str) and val.startswith("http"):
        return True
    return False

def extract_online_order_flag(val):
    """
    Return True if restaurant supports online ordering.
    SerpApi uses a URL string for 'order_online' when available.
    """
    if isinstance(val, str) and val.startswith("http"):
        return True
    return False

# ============================================================
# Helper: extract dine-in, takeout, delivery from service_options
# ============================================================
def extract_service_features(service_val):
    """
    Extract dine_in / takeout / delivery features from service_options dict.
    Delivery is True if ANY key containing “delivery” is True.
    """
    d = parse_dict(service_val)
    if not isinstance(d, dict):
        return None, None, None

    dine = d.get("dine_in", None)
    take = d.get("takeout", None)
    delivery = any("delivery" in k and v for k, v in d.items())

    return dine, take, delivery


# ============================================================
# Helper: convert “1 month ago”, “2 weeks ago” → actual datetime
# ============================================================
def parse_relative_date(s):
    """Convert SerpApi relative time strings into actual datetimes."""
    if not isinstance(s, str):
        return None

    s = s.lower().strip()
    now = datetime.now()
    parts = s.split()

    if len(parts) < 2:
        return None

    num_str = parts[0]
    unit = parts[1]

    if num_str == "a":
        num = 1
    else:
        try:
            num = int(num_str)
        except:
            return None

    if "day" in unit:
        return now - timedelta(days=num)
    if "week" in unit:
        return now - timedelta(weeks=num)
    if "month" in unit:
        return now - timedelta(days=30 * num)   # approx OK
    if "year" in unit:
        return now - timedelta(days=365 * num)

    return None


# ============================================================
# Helper: clean cuisine text
# ============================================================
def extract_cuisine(t):
    """Simplify raw cuisine/type text into a standardized cuisine label."""
    if pd.isna(t):
        return "Other"

    t = str(t).lower()

    # Explicit cuisine classification
    if "italian" in t: return "Italian"
    if "mediterranean" in t: return "Mediterranean"
    if "mexican" in t: return "Mexican"
    if "american" in t: return "American"
    if "japanese" in t or "sushi" in t: return "Japanese"
    if "chinese" in t: return "Chinese"
    if "thai" in t: return "Thai"
    if "indian" in t: return "Indian"
    if "cafe" in t or "coffee" in t: return "Cafe"
    if "bbq" in t or "barbecue" in t: return "BBQ"
    if "pizza" in t: return "Pizza"
    if "seafood" in t: return "Seafood"

    # If this type is too generic, classify as Other
    # e.g., "restaurant", "diner", "grill", "eatery"
    generic_words = ["Restaurant", "restaurant", "diner", "eatery", "grill", "food"]
    if any(word in t for word in generic_words):
        return "Other"

    # fallback → clean title-case string
    return t.title()


def parse_price_to_level(p):
    """
    Convert SerpApi price strings into a numeric price level.
    Examples:
      "$"      → 1
      "$$"     → 2
      "$$$"    → 3
      "$50–100" → (50+100)/2 = 75
    If parsing fails, returns None.
    """
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return None

    s = str(p).strip()

    # Pure '$', '$$', '$$$' style
    if set(s) == {"$"}:
        return len(s)

    # Ranged price like "$10–20" or "$15-30"
    nums = re.findall(r"\d+", s)
    if nums:
        vals = [int(x) for x in nums]
        return sum(vals) / len(vals)

    return None

# ============================================================
# MAIN CLEANING PROCESS
# ============================================================
def clean_and_save():

    # Ensure db exists
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"{DB_PATH} not found. Run save_raw_data.py first.")

    conn = sqlite3.connect(DB_PATH)

    # Load raw tables
    raw_places = pd.read_sql("SELECT * FROM raw_restaurants", conn)
    raw_reviews = pd.read_sql("SELECT * FROM raw_reviews", conn)

    # -----------------------------------------
    # CLEAN PLACES
    # -----------------------------------------
    places = raw_places.copy()

    # gps_coordinates → lat/lon
    def safe_lat(x):
        try:
            return eval(x).get("latitude")
        except:
            return None

    def safe_lon(x):
        try:
            return eval(x).get("longitude")
        except:
            return None

    places["latitude"] = places["gps_coordinates"].apply(safe_lat)
    places["longitude"] = places["gps_coordinates"].apply(safe_lon)
    places = places.dropna(subset=["latitude", "longitude"])

    # numeric
    places["rating"] = pd.to_numeric(places["rating"], errors="coerce")
    places["place_reviews_count"] = pd.to_numeric(
        places["reviews"], errors="coerce"
    ).fillna(0)

    if "price" in places.columns:
        places["price_level"] = places["price"].apply(parse_price_to_level)
    elif "price_level" in places.columns:
        # already numeric; just ensure it's numeric
        places["price_level"] = pd.to_numeric(places["price_level"], errors="coerce")
    else:
        places["price_level"] = None

    # cuisine
    places["cuisine"] = places["type"].apply(extract_cuisine)

    # service options
    places["dine_in"], places["takeout"], places["delivery"]= zip(
        *places["service_options"].apply(extract_service_features)
    )
    # ====== Reservation flag ======
    places["has_reserve_table"] = places["reserve_a_table"].apply(extract_reserve_flag)

        # NEW: Online order flag 
    if "order_online" in places.columns:
        places["has_online_order"] = places["order_online"].apply(extract_online_order_flag)
    else:
        places["has_online_order"] = False

    # NEW: convert bool-like columns to 0/1 integers
    bool_cols = ["dine_in", "takeout", "delivery", "has_reserve_table", "has_online_order"]
    for c in bool_cols:
        places[c] = places[c].fillna(False).astype(int)

    # NEW: simple convenience score = how many channels are available
    places["convenience_score"] = places[bool_cols].sum(axis=1)

    clean_places = places[[
        "place_id", "title", "rating", "place_reviews_count",
        "cuisine", "price_level", "address",
        "latitude", "longitude",
        "dine_in", "takeout", "delivery", "has_reserve_table", "has_online_order",   # NEW
        "convenience_score"
    ]].rename(columns={"title": "place_title"})

    
    # -----------------------------------------
    # CLEAN REVIEWS
    # -----------------------------------------
    reviews = raw_reviews.copy()

    # Extract reviewer name if review_user column exists
    def get_name(val):
        d = parse_dict(val)
        if isinstance(d, dict):
            return d.get("name")
        return None

    if "review_user" in reviews.columns:
        reviews["reviewer_name"] = reviews["review_user"].apply(get_name)
    else:
        # If the column does not exist, just create an empty reviewer_name
        reviews["reviewer_name"] = None

    # Convert relative date → actual datetime
    if "review_date" in reviews.columns:
        reviews["review_datetime"] = reviews["review_date"].apply(parse_relative_date)
    else:
        # Fallback: no date information available
        reviews["review_datetime"] = None

    # Keep only useful columns (select only those that actually exist)
    cols = []
    if "place_data_id" in reviews.columns:
        cols.append("place_data_id")
    if "place_title" in reviews.columns:
        cols.append("place_title")
    if "review_rating" in reviews.columns:
        cols.append("review_rating")
    if "review_text" in reviews.columns:
        cols.append("review_text")
    cols.extend(["reviewer_name", "review_datetime"])

    clean_reviews = reviews[cols].copy()

    # Rename place_data_id → place_id if present
    if "place_data_id" in clean_reviews.columns:
        clean_reviews = clean_reviews.rename(columns={"place_data_id": "place_id"})

    # -----------------------------------------
    # SAVE CLEANED TABLES
    # -----------------------------------------
    clean_places.to_sql("clean_restaurants", conn, if_exists="replace", index=False)
    clean_reviews.to_sql("clean_reviews", conn, if_exists="replace", index=False)

    conn.close()
    print("✔ Cleaned tables saved → clean_restaurants, clean_reviews")


if __name__ == "__main__":
    clean_and_save()