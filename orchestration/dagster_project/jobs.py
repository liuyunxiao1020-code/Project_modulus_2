from dagster import define_asset_job, AssetSelection

# Full pipeline job — runs all assets in order
full_pipeline_job = define_asset_job(
    name="full_pipeline_job",
    selection=AssetSelection.all(),
    description="Full pipeline: ingest → transform → test → analyze"
)

# Transformation only job — skips ingestion
transformation_job = define_asset_job(
    name="transformation_job",
    selection=AssetSelection.groups("transformation", "quality"),
    description="Run dbt models and tests only"
)