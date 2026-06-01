import os
import subprocess
import pandas as pd
from pathlib import Path
from google.cloud import bigquery
from dagster import asset, AssetExecutionContext, MetadataValue

# Full absolute paths — works regardless of working directory
DBT_EXECUTABLE  = "/home/liuyx/Project/Project_modulus_2/.venv/bin/dbt"
DBT_PROJECT_DIR = "/home/liuyx/Project/Project_modulus_2/dbt_project"
GCP_KEY_FILE    = "/home/liuyx/Project/Project_modulus_2/credentials/gcp-key.json"
RAW_DATA_PATH   = Path("/home/liuyx/Project/Project_modulus_2/data/raw")
PROJECT_ID      = "my-project-learning-496207"

# ── Asset 1: Raw data ingestion ───────────────────────────────────────
@asset(
    group_name="ingestion",
    description="Load all Olist CSV files into BigQuery raw tables"
)
def raw_data_ingested(context: AssetExecutionContext):
    from google.cloud import bigquery

    # Set credentials BEFORE creating client
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_KEY_FILE
    context.log.info(f"Using credentials: {GCP_KEY_FILE}")

    # Verify file exists before proceeding
    if not Path(GCP_KEY_FILE).exists():
        raise FileNotFoundError(f"GCP key file not found at: {GCP_KEY_FILE}")

    client = bigquery.Client(project=PROJECT_ID)
    context.log.info("BigQuery client created successfully")

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

    tables_loaded = 0
    total_rows    = 0

    for filename, table_name in CSV_TABLE_MAP.items():
        filepath = RAW_DATA_PATH / filename
        if not filepath.exists():
            context.log.warning(f"Skipped: {filename} not found")
            continue

        context.log.info(f"Loading {filename} → {table_name}")
        df = pd.read_csv(filepath)

        table_id   = f"{PROJECT_ID}.ecommerce_raw.{table_name}"
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",
            autodetect=True,
        )

        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()

        tables_loaded += 1
        total_rows    += len(df)
        context.log.info(f"  Done — {len(df):,} rows")

    context.add_output_metadata({
        "tables_loaded": MetadataValue.int(tables_loaded),
        "total_rows":    MetadataValue.int(total_rows),
    })

    return {"tables_loaded": tables_loaded, "total_rows": total_rows}


# ── Asset 2: dbt transformations ─────────────────────────────────────
@asset(
    group_name="transformation",
    description="Run dbt models to build star schema tables",
    deps=[raw_data_ingested]
)
def dbt_models_run(context: AssetExecutionContext):
    dbt_dir = DBT_PROJECT_DIR

    context.log.info("Running dbt models...")
    result = subprocess.run(
        ["dbt", "run", "--profiles-dir", dbt_dir],
        cwd=dbt_dir,
        capture_output=True,
        text=True
    )

    context.log.info(result.stdout)

    if result.returncode != 0:
        context.log.error(result.stderr)
        raise Exception(f"dbt run failed:\n{result.stderr}")

    context.add_output_metadata({
        "dbt_output": MetadataValue.text(result.stdout[-2000:])
    })

    return {"status": "success"}


# ── Asset 3: dbt tests ────────────────────────────────────────────────
@asset(
    group_name="quality",
    description="Run dbt data quality tests",
    deps=[dbt_models_run]
)
def dbt_tests_passed(context: AssetExecutionContext):
    dbt_dir = "/home/liuyx/Project/Project_modulus_2/dbt_project"

    context.log.info("Running dbt tests...")
    result = subprocess.run(
        ["dbt", "test", "--profiles-dir", dbt_dir],
        cwd=dbt_dir,
        capture_output=True,
        text=True
    )

    context.log.info(result.stdout)

    if result.returncode != 0:
        context.log.error(result.stderr)
        raise Exception(f"dbt test failed:\n{result.stderr}")

    context.add_output_metadata({
        "test_output": MetadataValue.text(result.stdout[-2000:])
    })

    return {"status": "all tests passed"}


# ── Asset 4: Data analysis ────────────────────────────────────────────
@asset(
    group_name="analysis",
    description="Run key business metrics analysis",
    deps=[dbt_tests_passed]
)
def business_metrics_computed(context: AssetExecutionContext):
    from google.cloud import bigquery

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/liuyx/Project/Project_modulus_2/credentials/gcp-key.json"
    client = bigquery.Client(project="my-project-learning-496207")

    # Monthly revenue
    query = """
        SELECT
            FORMAT_DATE('%Y-%m', purchased_at)  AS month,
            COUNT(DISTINCT order_id)            AS total_orders,
            ROUND(SUM(item_price), 2)           AS total_revenue
        FROM `my-project-learning-496207.ecommerce_marts.fact_orders`
        WHERE purchased_at IS NOT NULL
        GROUP BY month
        ORDER BY month DESC
        LIMIT 3
    """

    df = client.query(query).to_dataframe()
    context.log.info(f"Latest 3 months:\n{df.to_string()}")

    context.add_output_metadata({
        "latest_month_revenue": MetadataValue.float(
            float(df["total_revenue"].iloc[0])
        ),
        "latest_month_orders": MetadataValue.int(
            int(df["total_orders"].iloc[0])
        ),
    })

    return df.to_dict()