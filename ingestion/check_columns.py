import pandas as pd
from pathlib import Path

RAW_DATA_PATH = Path("data/raw")

files_to_check = [
    "product_category_name_translation.csv",
    "olist_products_dataset.csv",
    "olist_orders_dataset.csv",
]

for filename in files_to_check:
    filepath = RAW_DATA_PATH / filename
    if not filepath.exists():
        print(f"SKIPPED: {filename} not found")
        continue

    df = pd.read_csv(filepath)
    print(f"\n{'='*50}")
    print(f"File: {filename}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Shape: {df.shape}")
    print(f"First row:\n{df.head(1)}")