# src/api/fetch_data.py
import os
import pandas as pd
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

def fetch_api_data(query="restaurants", ll="@41.8781,-87.6298,14z"):
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise RuntimeError("Missing SERPAPI_KEY in .env")

    params = {
        "engine": "google_maps",
        "q": query,
        "ll": ll,
        "type": "search",
        "api_key": api_key
    }

    print("Fetching data from SerpApi ...")
    results = GoogleSearch(params).get_dict()
    data = results.get("local_results", [])

    os.makedirs("data", exist_ok=True)
    out_path = "data/raw_restaurants.csv"
    pd.DataFrame(data).to_csv(out_path, index=False)

    print(f"Fetched {len(data)} records → saved to {out_path}")
    return out_path

if __name__ == "__main__":
    fetch_api_data()