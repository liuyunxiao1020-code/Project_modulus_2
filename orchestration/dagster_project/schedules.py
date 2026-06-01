from dagster import ScheduleDefinition
from dagster_project.jobs import full_pipeline_job, transformation_job

daily_pipeline_schedule = ScheduleDefinition(
    job=full_pipeline_job,
    cron_schedule="0 0 * * *",
    name="daily_pipeline_schedule",
    description="Run full pipeline daily at midnight"
)

frequent_transform_schedule = ScheduleDefinition(
    job=transformation_job,
    cron_schedule="0 */6 * * *",
    name="frequent_transform_schedule",
    description="Run dbt transforms every 6 hours"
)