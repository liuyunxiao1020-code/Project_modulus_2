# Project_modulus_2
Project for modulus 2 
# Data Engineering Project

End-to-end data pipeline using the Brazilian E-Commerce (Olist) dataset.

## Setup

1. Clone the repo
2. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your credentials

## Running the pipeline

1. Ingest raw data: `python ingestion/ingest.py`
2. Run dbt transformations: `cd dbt_project && dbt run`
3. Run quality tests: `dbt test`
4. Open analysis: `jupyter notebook notebooks/analysis.ipynb`

## Architecture

See `docs/architecture.png` for the full data flow diagram.