# Notes

## Time spent

Approximately 6 hours total.

- Setup / Docker / environment: ~1 hour
- Extract & load: ~1.5 hours
- dbt: ~1 hour
- Airflow: ~1 hour
- Notebook / validation / cleanup: ~1.5 hours

## What I would do with more time

- Add more comprehensive data-quality checks, including reasonable range checks for weather metrics.
- Improve database loading efficiency by reusing a single database connection for a batch of rows.
- Add automated unit tests for the ingestion functions.
- Add more production-oriented observability and logging.

## Known gaps

- The Jupyter development server disables XSRF protection to allow the VS Code notebook kernel to connect to the local Docker Jupyter server. This is intended only for the local assessment environment and should not be used for a publicly exposed Jupyter server.
- The ingestion loader currently opens a database connection for each row rather than reusing one connection for the complete batch.
- The pipeline is intentionally small and does not include production-scale monitoring or alerting.

## AI-usage declaration

I used ChatGPT as a development aid during the assessment.

The main uses were:
- Clarifying assessment requirements and data-engineering concepts.
- Troubleshooting Docker, PostgreSQL, Airflow, dbt, and Jupyter configuration issues.
- Getting step-by-step guidance and small code suggestions while implementing the pipeline.
- Reviewing implementation choices and helping interpret error messages.
- Checking commands and validating expected behavior during development.

I implemented, tested, and validated the pipeline locally, including the extraction/load flow, dbt models and tests, Airflow DAG, backfill/rerun behavior, and notebook execution.