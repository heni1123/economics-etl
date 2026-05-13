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

4. Verify the data load:
   - Check the `public.fact_economic_indicators` table in PostgreSQL for the latest entries.

## Monitoring

### Metrics to Monitor
- Number of rows extracted and loaded.
- API response times and success rates.
- Database load times and query performance.

### Tools
- Use Prometheus and Grafana for real-time monitoring.
- Set up alerts for failure rates exceeding 5% or response times exceeding 2 seconds.

## Alerting

### Alert Configuration
- Configure alerts in Grafana for:
  - ETL job failures.
  - High latency in API responses.
  - Data quality issues (e.g., missing GDP or population data).

### Notification Channels
- Set up email notifications for critical alerts.
- Integrate with Slack for real-time updates.

## Rollback

### Rollback Procedure
1. Identify the last successful ETL run from the `etl_pipeline_runs` table.
2. Restore the `public.fact_economic_indicators` table from a backup if data integrity is compromised.
3. Re-run the ETL pipeline after addressing the identified issues.

### Backup Strategy
- Schedule daily backups of the PostgreSQL database.
- Use `pg_dump` for creating backups:
  ```bash
  pg_dump -U <username> -h <host> -F c -b -v -f "backup_file.backup" <database_name>
  ```

## Documentation
- Ensure all changes and procedures are documented in the repository's `docs` folder.
- Update the user manual for data analysts as needed.