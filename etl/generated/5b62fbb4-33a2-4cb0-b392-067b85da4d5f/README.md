# Global Economic Indicators ETL — Daily Refresh

## Overview
The Global Economic Indicators ETL project centralizes and analyzes global economic indicators such as GDP, population, and exchange rates from free public APIs into a PostgreSQL data warehouse for international comparative analysis.

## Architecture
The ETL pipeline consists of multiple components:
- **Data Sources**: APIs from the World Bank for GDP and population data, Exchange Rates API for currency conversion, and REST Countries API for country information.
- **Data Warehouse**: PostgreSQL 15 database with tables `fact_economic_indicators`, `fact_exchange_rates`, and `dim_country`.
- **ETL Process**: Extracts data from APIs, transforms it according to business rules, and loads it into the data warehouse.

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
   ```
   export GITHUB_TOKEN=<your_github_token>
   export DB_PASSWORD=<your_db_password>
   ```
2. Configure the database connection in the `config.py` file.

## Run
The ETL pipeline is scheduled to run daily. To execute the pipeline manually, run:
```
python etl_pipeline.py
```
The pipeline will extract data from the following sources:
- World Bank GDP: `https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD`
- World Bank Population: `https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL`
- Exchange Rates: `https://open.er-api.com/v6/latest/USD`
- REST Countries: `https://restcountries.com/v3.1/all`

## Testing
To run tests, execute:
```
pytest tests/
```
Ensure all tests pass before deploying changes.

## API Sources
- **World Bank GDP**: `GET https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD`
- **World Bank Population**: `GET https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL`
- **Exchange Rates API**: `GET https://open.er-api.com/v6/latest/USD`
- **REST Countries API**: `GET https://restcountries.com/v3.1/all`

## Troubleshooting
- Check the logs for any errors during the ETL process.
- Ensure that the API endpoints are accessible and returning valid data.
- Verify that the database connection parameters are correctly set in the configuration file.