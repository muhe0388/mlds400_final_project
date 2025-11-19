# Evanston Restaurant Insights --- MLDS 400 Final Project

## 📌 Overview

This project builds an **end-to-end data engineering pipeline** to
analyze how restaurant **quality**, **popularity**, **price**, and
**convenience** relate to each other in Evanston, IL. Using **SerpAPI**
to extract Google Maps restaurant and review data, the project explores
the central question:

> **"Is Evanston's most convenient food also its best food?"**

This repository includes: - API scraping scripts\
- Raw → cleaned SQLite database pipeline\
- A complete exploratory data analysis notebook\
- Visualizations aligned with the project plan\
- Fully reproducible instructions so anyone can run the project
end-to-end

------------------------------------------------------------------------

## 🗂️ Repository Structure

    mlds400_final_project/
    │
    ├── data/
    │   ├── restaurants.db
    │
    ├── notebooks/
    │   └── Evanston.ipynb
    │
    ├── src/  
    │   ├── db/
    │       ├── save_raw_data.py
    │       └── clean_data.py 
    ├── requirements.txt
    └── README.md

------------------------------------------------------------------------

## 📡 Data Sources

### **Restaurants Table (raw)**

Extracted via SerpAPI: - Name\
- Rating\
- Cuisine/type text\
- Price\
- \# of reviews\
- Dine-in / Takeout / Delivery\
- Reservation URL\
- Online ordering URL\
- Address\
- GPS coordinates\
- Tags

### **Reviews Table (raw)**

Extracted per restaurant: - Review rating\
- Review text\
- User info\
- Relative review date (e.g., "2 months ago")

------------------------------------------------------------------------

## ⚙️ Pipeline Overview (End-to-End)

### **1. 💻 API Scraping Layer (JSON → CSV)**

`src/api/serp_api_scraper.py`\
- Calls SerpAPI to fetch restaurant search results and review text\
- Saves output into:\
- `data/raw_restaurants.csv`\
- `data/raw_reviews.csv`

------------------------------------------------------------------------

### **2. 🟦 Raw Data Layer (CSV → SQLite Raw Tables)**

`src/db/save_raw_data.py`\
Creates raw DB tables with minimal processing: - Extracts GPS
latitude/longitude\
- Converts object fields to strings\
- Parses reviewer info (`review_user_name`, `review_user_link`)\
- Stores **raw tables:**\
- `raw_restaurants`\
- `raw_reviews`

------------------------------------------------------------------------

### **3. 🟩 Clean Data Layer (Raw DB → Cleaned DB Tables)**

`src/db/clean_data.py`\
Transforms raw tables into fully standardized analytics tables.

Cleans & standardizes: - GPS fields\
- Numeric fields (rating, reviews)\
- Price → numeric price levels\
- Cuisine categories\
- Service options (dine-in, takeout, delivery)\
- Reservation + online ordering flags\
- Convenience score\
- Review text, reviewer name, timestamps

Creates **clean tables:** - `clean_restaurants`\
- `clean_reviews`

------------------------------------------------------------------------

### **4. 📊 Analysis Layer (Clean DB → Visualizations)**

`notebooks/Evanston.ipynb`\
Includes:\
- Restaurant landscape map / bubble plot\
- Hidden gems vs hype magnets\
- Convenience impact analysis\
- Cuisine value analysis\
- Review sentiment & keyword trends\
- Final quality--convenience quadrant

------------------------------------------------------------------------

## ▶️ How to Run the Entire Pipeline

### **1. Clone the Repo**

``` bash
git clone https://github.com/YOUR_USERNAME/mlds400_final_project.git
cd mlds400_final_project
```

### **2. Install Dependencies**

``` bash
pip install -r requirements.txt
```

### **3. Add SerpAPI Key**

Create `.env`:

    SERPAPI_KEY=your_key_here

### **4. Scrape Data (Optional)**

``` bash
python src/api/serp_api_scraper.py
```

### **5. Build RAW Database Layer**

``` bash
python src/db/save_raw_data.py
```

### **6. Build CLEAN Database Layer**

``` bash
python src/db/clean_data.py
```

### **7. Run EDA Notebook**

``` bash
jupyter notebook notebooks/Evanston.ipynb
```

------------------------------------------------------------------------

## 📊 Key Insights (Replace with Real Findings)

-   Many high-quality restaurants are underrated ("hidden gems")\
-   Online ordering boosts popularity more than quality\
-   Certain cuisines have strong value ratings\
-   Review keywords reveal convenience-driven vs quality-driven
    restaurants

------------------------------------------------------------------------

## 🧪 Requirements

    pandas
    numpy
    matplotlib
    seaborn
    folium
    geopy
    requests
    python-dotenv
    textblob
    notebook
    sqlite3

------------------------------------------------------------------------

## 👥 Contributors

  -----------------------------------------------------------------------
  Name                                         Role
  -------------------------------------------- --------------------------
  Paul                                         Story framing, EDA plan,
                                               presentation

  Mu                                           Data collection, raw→clean
                                               transformations, EDA

  Ashwath                                      GitHub architecture,
                                               pipeline documentation,
                                               notebook integration
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 📄 License

MIT License (or your preference)

------------------------------------------------------------------------

## 🎉 Final Notes

This project demonstrates a fully operational data engineering
workflow:\
**Scraping → Raw DB → Clean DB → Analysis → Insights**\
Future extensions may include dashboards, extended NLP, or multi-city
comparisons.
