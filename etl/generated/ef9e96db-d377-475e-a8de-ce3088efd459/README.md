# Global Economic Indicators ETL — Daily Refresh

## Overview
The Global Economic Indicators ETL project is designed to centralize and analyze global economic indicators such as GDP, population, and exchange rates from free public APIs into a PostgreSQL data warehouse for international comparative analysis.

## Architecture
The ETL pipeline consists of four main components:
1. Data Extraction: Fetching data from various APIs.
2. Data Transformation: Processing and cleaning the data.
3. Data Loading: Inserting the transformed data into PostgreSQL tables.
4. Logging and Monitoring: Keeping track of the ETL process and handling errors.

## Data Sources
- **World Bank GDP**: [API](https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD)
- **World Bank Population**: [API](https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL)
- **Exchange Rates API**: [API](https://open.er-api.com/v6/latest/USD)
- **REST Countries API**: [API](https://restcountries.com/v3.1/all)

## Target Tables
- `fact_economic_indicators`
- `fact_exchange_rates`
- `dim_country`

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
   - `GITHUB_TOKEN`: Your GitHub Personal Access Token.
   - `DB_PASSWORD`: Your PostgreSQL database password.

## Running
To execute the ETL pipeline, run the following command:
```
python etl_pipeline.py
```
The pipeline can be executed on-demand as per the requirements.

## Testing
Unit tests are included in the `tests` directory. To run the tests, use:
```
pytest tests/
```

## Troubleshooting
- Check the logs for any errors during the ETL process.
- Ensure that the environment variables are correctly set.
- Verify the API endpoints for any changes or downtime.
- For network-related issues, consider implementing exponential backoff for retries.