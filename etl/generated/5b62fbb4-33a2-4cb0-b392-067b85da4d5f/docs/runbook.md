# ETL Pipeline Operational Runbook

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
2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure the database connection in the `.env` file:
   ```
   DATABASE_URL=postgresql://user:DB_PASSWORD@localhost:5432/economic_data
   ```
4. Run the ETL pipeline:
   ```bash
   python etl_pipeline.py
   ```

## Monitoring

### Metrics to Monitor
- ETL execution time
- Number of rows extracted and loaded
- API response times and error rates

### Tools
- Use Prometheus and Grafana for real-time monitoring.
- Set up alerts for failures and performance degradation.

## Alerting

### Alert Configuration
- Configure alerts for:
  - ETL job failures
  - High error rates from APIs
  - Data quality issues (e.g., missing GDP or population data)

### Notification Channels
- Use Slack or email for alert notifications.
- Integrate with monitoring tools to send alerts.

## Rollback

### Rollback Procedure
1. Identify the last successful ETL run from the `etl_pipeline_runs` table.
2. Restore the database to the state before the failed ETL run:
   ```sql
   DELETE FROM public.fact_economic_indicators
   WHERE (country_code, year) IN (
       SELECT country_code, year
       FROM public.etl_pipeline_runs
       WHERE status = 'failed'
   );
   ```
3. Re-run the ETL pipeline after addressing the issues.

### Backup Strategy
- Schedule daily backups of the PostgreSQL database.
- Store backups in a secure location for recovery.