# src/db

# src/db/save_raw_data.py

import os
import sqlite3
import ast
import pandas as pd

# Resolve paths: project root / data / db
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "restaurants.db")


def _coerce_object_columns_to_str(df: pd.DataFrame) -> pd.DataFrame:
    """
    For the raw layer: ensure any non-numeric columns are stored as TEXT in SQLite
    by converting them to string. This safely handles list/dict-like values
    that might still appear as Python objects.
    """
    for col in df.columns:
        if pd.api.types.is_integer_dtype(df[col]) or pd.api.types.is_float_dtype(df[col]):
            continue
        df[col] = df[col].astype(str)
    return df


# ------------------------- Places (restaurants) ------------------------- #

def _parse_gps_coordinates(val):
    """
    raw_restaurants.gps_coordinates looks like:
      "{'latitude': 42.04619, 'longitude': -87.6815}"
    or a dict. We extract latitude / longitude into two new columns.
    """
    if isinstance(val, dict):
        return val.get("latitude"), val.get("longitude")

    if isinstance(val, str):
        try:
            obj = ast.literal_eval(val)
            if isinstance(obj, dict):
                return obj.get("latitude"), obj.get("longitude")
        except Exception:
            return None, None
    return None, None


def prepare_raw_restaurants():
    """
    Read raw_restaurants.csv, add latitude/longitude columns,
    and return a DataFrame ready to be written into SQLite.
    """
    restaurants_csv = os.path.join(DATA_DIR, "raw_restaurants.csv")
    if not os.path.exists(restaurants_csv):
        print("raw_restaurants.csv not found, skipping raw_restaurants table.")
        return None

    df = pd.read_csv(restaurants_csv)

    # Extract GPS lat/lon from gps_coordinates column (if present)
    if "gps_coordinates" in df.columns:
        lats = []
        lngs = []
        for v in df["gps_coordinates"]:
            lat, lng = _parse_gps_coordinates(v)
            lats.append(lat)
            lngs.append(lng)
        df["latitude"] = lats
        df["longitude"] = lngs

    # data_cid save as TEXT
    if "data_cid" in df.columns:
        df["data_cid"] = df["data_cid"].astype(str)

    # Light normalization for raw layer: keep everything but coerce to string where needed
    df = _coerce_object_columns_to_str(df)

    return df


# ------------------------- Reviews ------------------------- #

def prepare_raw_reviews():
    """
    Read raw_reviews.csv, flatten review_user dict into two columns
    (review_user_name, review_user_link), then return DataFrame
    ready to be written into SQLite.
    """
    reviews_csv = os.path.join(DATA_DIR, "raw_reviews.csv")
    if not os.path.exists(reviews_csv):
        print("raw_reviews.csv not found, skipping raw_reviews table.")
        return None

    df = pd.read_csv(reviews_csv)

    # If review_user is stored as a dict-like string, parse it
    if "review_user" in df.columns:
        def ensure_dict(x):
            if isinstance(x, dict):
                return x
            if isinstance(x, str):
                try:
                    return ast.literal_eval(x)
                except Exception:
                    return None
            return None

        users = df["review_user"].apply(ensure_dict)

        df["review_user_name"] = users.apply(
            lambda u: u.get("name") if isinstance(u, dict) else None
        )
        df["review_user_link"] = users.apply(
            lambda u: u.get("link") if isinstance(u, dict) else None
        )

        # We can drop the original dict column in the raw layer DB
        df = df.drop(columns=["review_user"])

    # Light normalization for raw layer
    df = _coerce_object_columns_to_str(df)

    return df


# ------------------------- Main save function ------------------------- #

def save_raw_tables():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # raw_restaurants
    df_rest = prepare_raw_restaurants()
    if df_rest is not None:
        df_rest.to_sql("raw_restaurants", conn, if_exists="replace", index=False)
        print(f"Saved raw_restaurants → {DB_PATH} (rows={len(df_rest)})")

    # raw_reviews
    df_reviews = prepare_raw_reviews()
    if df_reviews is not None:
        df_reviews.to_sql("raw_reviews", conn, if_exists="replace", index=False)
        print(f"Saved raw_reviews → {DB_PATH} (rows={len(df_reviews)})")

    conn.close()


if __name__ == "__main__":
    save_raw_tables()