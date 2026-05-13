# Global Economic Indicators ETL — Daily Refresh

## Overview
The Global Economic Indicators ETL project is designed to centralize and analyze global economic indicators such as GDP, population, and exchange rates from free public APIs into a PostgreSQL data warehouse. This pipeline facilitates comparative international analysis and supports economic research.

## Architecture
The ETL pipeline consists of four main components:
1. **Data Extraction**: Fetches data from various APIs including the World Bank API for GDP and population, Exchange Rates API, and REST Countries API.
2. **Data Transformation**: Processes and transforms the extracted data to ensure it meets the required schema and business rules.
3. **Data Loading**: Loads the transformed data into the PostgreSQL database, specifically into the `public.fact_economic_indicators`, `public.fact_exchange_rates`, and `public.dim_country` tables.
4. **Logging and Monitoring**: Tracks the ETL process, logging execution details in the `etl_pipeline_runs` table for auditing and troubleshooting.

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
   - `GITHUB_TOKEN`: Your GitHub Personal Access Token.
   - `DB_PASSWORD`: The password for your PostgreSQL database.
2. Configure the database connection in the `config.py` file.

## Run
The ETL pipeline is scheduled to run daily at midnight UTC. You can manually trigger the ETL process using the following command:
```
python etl_pipeline.py
```

## Testing
To run the tests, execute:
```
pytest tests/
```
Ensure that all tests pass before deploying changes to production.

## API Sources
1. **World Bank GDP API**: 
   - URL: https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD
   - Method: GET
   - Description: Fetches GDP data from the World Bank.
   
2. **World Bank Population API**: 
   - URL: https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL
   - Method: GET
   - Description: Fetches population data from the World Bank.
   
3. **Exchange Rates API**: 
   - URL: https://open.er-api.com/v6/latest/USD
   - Method: GET
   - Description: Provides current exchange rates.
   
4. **REST Countries API**: 
   - URL: https://restcountries.com/v3.1/all
   - Method: GET
   - Description: Retrieves information about countries.

## Troubleshooting
- **Common Issues**:
  - If the ETL process fails, check the logs in the `etl_pipeline_runs` table for error messages.
  - Ensure that all environment variables are correctly set.
  - Verify network connectivity to the API endpoints.
- **Retry Mechanism**: The pipeline includes an exponential backoff strategy for handling API timeouts and network errors (1s, 2s, 4s).