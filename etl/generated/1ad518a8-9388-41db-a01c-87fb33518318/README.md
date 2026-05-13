# Global Economic Indicators ETL — Daily Refresh

## Overview
The Global Economic Indicators ETL project centralizes and analyzes global economic indicators such as GDP, population, and exchange rates from free public APIs into a PostgreSQL data warehouse for international comparative analysis.

## Architecture
The ETL pipeline consists of four main components:
1. **Data Extraction**: Fetches data from the World Bank API for GDP and population, Exchange Rates API, and REST Countries API.
2. **Data Transformation**: Processes and transforms the data according to business rules, ensuring data quality and compliance with specified formats.
3. **Data Loading**: Loads the transformed data into PostgreSQL tables: `public.fact_economic_indicators`, `public.fact_exchange_rates`, and `public.dim_country`.
4. **Logging and Auditing**: Records each ETL run in the `etl_pipeline_runs` table for auditing purposes.

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/heni1123/economics-etl.git
   cd economics-etl
   ```
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration
1. Set up environment variables:
   ```
   export GITHUB_TOKEN=<your_github_token>
   export DB_PASSWORD=<your_database_password>
   ```
2. Configure the PostgreSQL connection settings in the `config.py` file.

## Run
The ETL pipeline is scheduled to run daily at 2:00 AM UTC. You can manually trigger the ETL process using:
```
python etl_pipeline.py
```

## Testing
To run the tests, execute:
```
pytest tests/
```
Ensure that all tests pass before deploying changes.

## API Sources
1. **World Bank GDP**: 
   - URL: https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD
   - Method: GET
   - Auth: None
2. **World Bank Population**: 
   - URL: https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL
   - Method: GET
   - Auth: None
3. **Exchange Rates API**: 
   - URL: https://open.er-api.com/v6/latest/USD
   - Method: GET
   - Auth: None
4. **REST Countries API**: 
   - URL: https://restcountries.com/v3.1/all
   - Method: GET
   - Auth: None

## Troubleshooting
- **Common Issues**:
  - If the ETL process fails, check the logs in the `etl_pipeline_runs` table for error messages.
  - Ensure that the PostgreSQL database is running and accessible.
  - Verify that the API endpoints are reachable and returning valid responses.
- **Logging**: All ETL runs are logged for auditing and troubleshooting purposes. Check the logs for details on data extraction and loading statuses.