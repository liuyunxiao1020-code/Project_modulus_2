from dagster import Definitions
from dagster_project.assets import (
    raw_data_ingested,
    dbt_models_run,
    dbt_tests_passed,
    business_metrics_computed
)
from dagster_project.jobs import full_pipeline_job, transformation_job
from dagster_project.schedules import daily_pipeline_schedule, frequent_transform_schedule

defs = Definitions(
    assets=[
        raw_data_ingested,
        dbt_models_run,
        dbt_tests_passed,
        business_metrics_computed,
    ],
    jobs=[
        full_pipeline_job,
        transformation_job,
    ],
    schedules=[
        daily_pipeline_schedule,
        frequent_transform_schedule,
    ],
)