# ETL Operational Runbook

## Deployment

### Prerequisites
- Ensure PostgreSQL 15 is installed and configured.
- Set environment variables:
  - `GITHUB_TOKEN`: GitHub Personal Access Token
  - `DB_PASSWORD`: Database Password

### Deployment Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/heni1123/economics-etl.git
   cd economics-etl
   ```
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the ETL pipeline:
   ```bash
   python etl_pipeline.py
   ```

## Monitoring

### Metrics to Monitor
- Number of rows extracted and loaded.
- API response times and success rates.
- Database connection health.

### Tools
- Use Prometheus and Grafana for real-time monitoring.
- Set up alerts for failure rates exceeding 5%.

## Alerting

### Alert Configuration
- Configure alerts for:
  - ETL job failures.
  - High latency in API responses.
  - Database connection issues.

### Notification Channels
- Use Slack or email for alert notifications.
- Set up webhook integrations for real-time alerts.

## Rollback

### Rollback Procedure
1. Identify the last successful ETL run from the `etl_pipeline_runs` table.
2. Restore the database to the state before the failed ETL run:
   ```sql
   DELETE FROM public.fact_economic_indicators
   WHERE (country_code, year) IN (
       SELECT country_code, year FROM public.etl_pipeline_runs
       WHERE status = 'failed' AND run_id = 'LAST_SUCCESSFUL_RUN_ID'
   );
   ```
3. Re-run the ETL pipeline after addressing the issues.

### Verification
- Check the `etl_pipeline_runs` table for the status of the latest run.
- Validate data integrity in the `fact_economic_indicators` table.