# Operational Runbook for Global Economic Indicators ETL

## Deployment

1. **Prerequisites**
   - Ensure the following environment variables are set:
     - `GITHUB_TOKEN`: GitHub Personal Access Token for repository access.
     - `DB_PASSWORD`: Password for the PostgreSQL database.

2. **Clone the Repository**
   ```bash
   git clone https://github.com/heni1123/economics-etl.git
   cd economics-etl
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   - Ensure PostgreSQL is running and accessible.
   - Create the necessary database and tables:
   ```sql
   CREATE TABLE IF NOT EXISTS public.fact_economic_indicators (
       country_code VARCHAR(3) NOT NULL,
       country_name VARCHAR(100) NOT NULL,
       year INTEGER NOT NULL,
       gdp_usd NUMERIC(20,2),
       gdp_billions NUMERIC(15,2),
       population BIGINT,
       gdp_per_capita NUMERIC(12,2),
       gdp_growth_yoy NUMERIC(8,4),
       population_growth_yoy NUMERIC(8,4),
       economic_size_category VARCHAR(20),
       PRIMARY KEY (country_code, year)
   );
   ```

5. **Run the ETL Pipeline**
   - Execute the ETL script:
   ```bash
   python etl_pipeline.py
   ```

## Monitoring

1. **Log Files**
   - Monitor the log files generated during the ETL run for any errors or warnings.
   - Logs are stored in the `logs/` directory.

2. **Database Monitoring**
   - Check the `etl_pipeline_runs` table for the status of the last ETL run:
   ```sql
   SELECT * FROM etl_pipeline_runs ORDER BY run_time DESC LIMIT 10;
   ```

3. **API Usage**
   - Monitor API usage for the Exchange Rates API to ensure it does not exceed the limit of 1500 requests per month.

## Alerting

1. **Error Notifications**
   - Set up alerts to notify the team via email or messaging service (e.g., Slack) if the ETL pipeline fails.
   - Use monitoring tools like Prometheus or Grafana to visualize ETL performance metrics.

2. **Threshold Alerts**
   - Configure alerts for data quality issues, such as:
     - Less than 80% of expected rows loaded.
     - Outliers detected in `gdp_per_capita` or `population`.

## Rollback

1. **Rollback Strategy**
   - In case of a failure, the last successful ETL run can be restored from the `fact_economic_indicators` table.
   - Use the following SQL command to revert to the last known good state:
   ```sql
   DELETE FROM public.fact_economic_indicators WHERE year = <year_to_rollback>;
   ```

2. **Backup Procedures**
   - Regularly back up the `fact_economic_indicators` table to ensure data can be restored if needed.
   ```sql
   CREATE TABLE public.fact_economic_indicators_backup AS TABLE public.fact_economic_indicators;
   ```

3. **Post-Rollback Verification**
   - After rollback, verify the integrity of the data and ensure that the ETL pipeline can run successfully again.