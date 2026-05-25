import os
import pandas as pd
from google.cloud import bigquery, storage
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

PROJECT_ID = os.getenv('GCP_PROJECT_ID')
DATASET    = os.getenv('GCP_DATASET')
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

client = bigquery.Client(project=PROJECT_ID)

RAW_DATA_PATH = Path("data/raw")

CSV_TABLE_MAP = {
    "olist_orders_dataset.csv":              "raw_orders",
    "olist_order_items_dataset.csv":         "raw_order_items",
    "olist_customers_dataset.csv":           "raw_customers",
    "olist_products_dataset.csv":            "raw_products",
    "olist_sellers_dataset.csv":             "raw_sellers",
    "olist_order_payments_dataset.csv":      "raw_order_payments",
    "olist_order_reviews_dataset.csv":       "raw_order_reviews",
    "olist_geolocation_dataset.csv":         "raw_geolocation",
    "product_category_name_translation.csv": "raw_category_translation",
}

def ingest_all():
    # Create dataset if it doesn't exist
    dataset_ref = bigquery.Dataset(f"{PROJECT_ID}.{DATASET}")
    dataset_ref.location = "US"
    client.create_dataset(dataset_ref, exists_ok=True)
    print(f"Dataset `{DATASET}` ready.")

    for filename, table_name in CSV_TABLE_MAP.items():
        filepath = RAW_DATA_PATH / filename
        if not filepath.exists():
            print(f"SKIPPED: {filename} not found")
            continue

        print(f"Loading {filename} → {DATASET}.{table_name}...")
        df = pd.read_csv(filepath, header=0)

        table_id = f"{PROJECT_ID}.{DATASET}.{table_name}"

        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",  # replace on re-run
            autodetect=True,                     # auto-detect column types
        )

        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()  # wait for job to finish

        print(f"  Done — {len(df):,} rows loaded")

if __name__ == "__main__":
    ingest_all()
    print("\nAll tables ingested into BigQuery successfully.")
    
  