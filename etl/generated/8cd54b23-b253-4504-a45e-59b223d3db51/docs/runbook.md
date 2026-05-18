# Operational Runbook for Global Economic Indicators ETL

## Deployment

1. **Prerequisites**
   - Ensure the following environment variables are set:
     - `GITHUB_TOKEN`: GitHub Personal Access Token
     - `DB_PASSWORD`: Database Password
   - Ensure PostgreSQL 15 is installed and running.

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
   - Connect to PostgreSQL and create the necessary tables:
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
   - Use PostgreSQL monitoring tools to check the performance of the `fact_economic_indicators` table.
   - Ensure that the table is updated correctly after each ETL run.

3. **API Usage**
   - Monitor the API usage for the Exchange Rates API to ensure it does not exceed the limit of 1500 requests/month.

## Alerting

1. **Error Notifications**
   - Set up alerts to notify the team via email or Slack if the ETL process fails.
   - Use a monitoring tool like Prometheus or Grafana to visualize ETL performance metrics.

2. **Database Alerts**
   - Configure PostgreSQL to send alerts for any failed transactions or errors during data insertion.

## Rollback

1. **Rollback Strategy**
   - In case of a failure during the ETL process, the last successful run can be restored from the `etl_pipeline_runs` table.
   - Maintain a backup of the `fact_economic_indicators` table before each ETL run.

2. **Restore Command**
   - To restore the previous state of the database:
   ```sql
   DELETE FROM public.fact_economic_indicators WHERE year = <year_to_rollback>;
   INSERT INTO public.fact_economic_indicators (country_code, country_name, year, gdp_usd, gdp_billions, population, gdp_per_capita, gdp_growth_yoy, population_growth_yoy, economic_size_category)
   SELECT * FROM backup_table WHERE year = <year_to_rollback>;
   ```

3. **Post-Rollback Verification**
   - Verify the integrity of the data after rollback by running validation queries to ensure data quality and consistency.