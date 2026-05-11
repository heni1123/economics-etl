# README.md

## Overview
This ETL pipeline centralizes and analyzes global economic indicators such as GDP, population, and exchange rates from free public APIs into a PostgreSQL data warehouse for international comparative analysis.

## Architecture
The ETL pipeline consists of multiple components:
- **Data Sources**: 
  - World Bank API for GDP and population data
  - Exchange Rates API for currency conversion rates
  - REST Countries API for country information
- **Data Warehouse**: PostgreSQL 15 with the following tables:
  - `public.fact_economic_indicators`
  - `public.fact_exchange_rates`
  - `public.dim_country`
- **Logging and Monitoring**: Each ETL run is logged in the `etl_pipeline_runs` table for auditing and error tracking.

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/heni1123/economics-etl.git
   cd economics-etl
   ```
2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration
1. Set up environment variables:
   - `GITHUB_TOKEN`: Your GitHub Personal Access Token
   - `DB_PASSWORD`: Your PostgreSQL database password
2. Configure the database connection in the `config.py` file.

## Run
The ETL pipeline is scheduled to run daily at midnight using a cron job:
```
0 0 * * * /usr/bin/python3 /path/to/your/script.py
```
To run the pipeline manually, execute:
```
python script.py
```

## Testing
To run tests, use:
```
pytest tests/
```
Ensure all tests pass before deploying changes.

## API Sources
- **World Bank GDP**: [API](https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD)
- **World Bank Population**: [API](https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL)
- **Exchange Rates**: [API](https://open.er-api.com/v6/latest/USD)
- **REST Countries**: [API](https://restcountries.com/v3.1/all)

## Troubleshooting
- Check the logs in the `etl_pipeline_runs` table for any errors during execution.
- Ensure all environment variables are set correctly.
- Verify API availability and response formats. If an API fails, the pipeline will retry with exponential backoff (1s, 2s, 4s).