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

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the ETL pipeline:
   ```bash
   python etl_pipeline.py
   ```

## Monitoring

### Logging
- The ETL process logs all operations in `etl_logs.log`.
- Monitor the log file for:
  - Successful data extraction and loading.
  - Errors and warnings during execution.

### Metrics
- Track the number of rows extracted and loaded.
- Monitor the completion rates of API calls.

## Alerting

### Error Notifications
- Set up alerts for failures in the ETL process:
  - Use a monitoring tool (e.g., Prometheus, Grafana) to track the status of the ETL jobs.
  - Configure alerts for:
    - API call failures.
    - Data validation errors (e.g., GDP or population < 0).

### Email Notifications
- Configure email notifications for critical errors:
  - Use a service like SendGrid or SMTP to send alerts.

## Rollback

### Rollback Procedure
1. Identify the last successful ETL run from `etl_pipeline_runs` table.
2. Restore the database to the state before the last ETL run:
   ```sql
   DELETE FROM public.fact_economic_indicators
   WHERE (country_code, year) IN (
       SELECT country_code, year
       FROM public.etl_pipeline_runs
       WHERE run_id = 'last_successful_run_id'
   );
   ```

3. Re-run the ETL pipeline after resolving the issues.

### Backup Strategy
- Regularly back up the PostgreSQL database to prevent data loss.
- Use the following command to create a backup:
  ```bash
  pg_dump -U username -h hostname -F c -b -v -f "backup_file.backup" dbname
  ```

## Troubleshooting
- Check `etl_logs.log` for detailed error messages.
- Validate API responses against expected formats.
- Ensure all environment variables are correctly set.