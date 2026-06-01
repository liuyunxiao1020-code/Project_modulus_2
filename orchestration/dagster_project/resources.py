import os
from dagster import ConfigurableResource
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

class BigQueryResource(ConfigurableResource):
    project_id: str
    keyfile_path: str

    def get_client(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.keyfile_path
        return bigquery.Client(project=self.project_id)


# Shared config values
BIGQUERY_RESOURCE = BigQueryResource(
    project_id="my-project-learning-496207",
    keyfile_path="credentials/gcp-key.json"
)

DBT_PROJECT_DIR  = os.path.abspath("dbt_project")
DBT_PROFILES_DIR = os.path.abspath("dbt_project")