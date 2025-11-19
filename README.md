# Evanston Restaurant Insights --- MLDS 400 Final Project

## 📌 Overview

This project builds an **end-to-end data engineering pipeline** to
analyze how restaurant **quality**, **popularity**, **price**, and
**convenience** relate to each other in Evanston, IL. Using SerpAPI to
extract Google Maps restaurant and review data, we explore the central
question:

> **"Is Evanston's most convenient food also its best food?"**

This repo includes: - Data ingestion & cleaning scripts\
- A complete EDA notebook\
- Visualizations & insights\
- Reproducible instructions so anyone can run the project end-to-end

------------------------------------------------------------------------

## 🗂️ Repository Structure

    mlds400_final_project/
    │
    ├── data/
    │   ├── restaurants.csv
    │   ├── reviews.csv
    │
    ├── notebooks/
    │   └── Evanston.ipynb
    │
    ├── src/
    │   ├── api/
    │   │   └── serp_api_scraper.py
    │   ├── cleaning/
    │   │   └── clean_restaurants.py
    │   ├── analysis/
    │   │   └── eda_helpers.py
    │   └── utils/
    │       └── geocoding.py
    │
    ├── requirements.txt
    └── README.md

------------------------------------------------------------------------

## 📡 Data Sources

### **Restaurants Table**

-   Name\
-   Rating\
-   Cuisine\
-   Price per person\
-   Number of reviews\
-   Dine-in availability\
-   Reservation availability\
-   Online ordering availability\
-   Tags & address

### **Reviews Table**

-   Review rating\
-   Reviewer\
-   Date posted\
-   Review text\
-   (optional) Sentiment & keywords

Data is scraped via **SerpAPI → Google Maps Reviews API**.

------------------------------------------------------------------------

## ⚙️ Pipeline Overview

### **1. Data Collection**

`src/api/serp_api_scraper.py`\
- Queries Google Maps\
- Extracts restaurant & review data\
- Saves raw JSON → CSV

### **2. Data Cleaning**

`src/cleaning/clean_restaurants.py`\
- Standardizes price ranges\
- Cleans categories\
- Processes timestamps\
- Cleans text\
- Removes duplicates

### **3. Exploratory Data Analysis**

`notebooks/Evanston.ipynb` contains visualizations such as:\
- Bubble plots / maps\
- Quality vs popularity (hidden gems vs hype magnets)\
- Convenience feature analysis\
- Cuisine value analysis\
- Review sentiment over time\
- Final synthesis chart

------------------------------------------------------------------------

## ▶️ How to Run This Project

### **1. Clone the Repo**

``` bash
git clone https://github.com/YOUR_USERNAME/mlds400_final_project.git
cd mlds400_final_project
```

### **2. Install Requirements**

``` bash
pip install -r requirements.txt
```

### **3. Add SerpAPI Key**

Create a `.env` file:

    SERPAPI_KEY=your_key_here

### **4. Collect New Data (Optional)**

``` bash
python src/api/serp_api_scraper.py
```

### **5. Clean Data**

``` bash
python src/cleaning/clean_restaurants.py
```

### **6. Run EDA**

``` bash
jupyter notebook notebooks/Evanston.ipynb
```

------------------------------------------------------------------------

## 📊 Key Insights (Summaries)

> Replace with real findings after running the notebook.

-   Many high-quality restaurants are underrated ("hidden gems").\
-   Convenience features correlate strongly with popularity---not
    quality.\
-   Certain cuisines offer unusually strong value relative to price.\
-   Review text keywords confirm trends: popular spots emphasize
    convenience; hidden gems emphasize taste & authenticity.

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

------------------------------------------------------------------------

## 👥 Contributors

  Name      Role
  --------- --------------------------------------------------
  Paul      Story framing, EDA plan, presentation
  Mu        Data collection, cleaning, EDA
  Ashwath   GitHub repo, documentation, engineering pipeline

------------------------------------------------------------------------

## 📄 License

MIT License (or your choice).

------------------------------------------------------------------------

## 🎉 Final Notes

This project demonstrates a full data engineering workflow: ingestion →
cleaning → EDA → insights.\
Future extensions may include dashboards, LLM-based review
summarization, or automated geocoding.
