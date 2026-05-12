# ETL Pipeline for Economic Data

## Overview
This ETL pipeline centralizes and analyzes global economic indicators such as GDP, population, and exchange rates from free public APIs into a PostgreSQL data warehouse for international comparative analysis.

## Architecture
The pipeline extracts data from the following APIs:
- World Bank API for GDP: `https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD`
- World Bank API for Population: `https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL`
- Exchange Rates API: `https://open.er-api.com/v6/latest/USD`
- REST Countries API: `https://restcountries.com/v3.1/all`

The data is loaded into the following PostgreSQL tables:
- `public.fact_economic_indicators`
- `public.fact_exchange_rates`
- `public.dim_country`

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
Set the following environment variables:
- `GITHUB_TOKEN`: Your GitHub Personal Access Token.
- `DB_PASSWORD`: Your PostgreSQL database password.

## Run
The ETL pipeline is scheduled to run daily at midnight using a cron job:
```
0 0 * * * /usr/bin/python3 /path/to/your/script.py
```

## Testing
To run tests, execute the following command:
```
pytest tests/
```

## API Sources
- **World Bank GDP API**: `GET https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=1000&date=2020:2023`
- **World Bank Population API**: `GET https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=1000&date=2020:2023`
- **Exchange Rates API**: `GET https://open.er-api.com/v6/latest/USD`
- **REST Countries API**: `GET https://restcountries.com/v3.1/all`

## Troubleshooting
- Ensure all environment variables are set correctly.
- Check the logs for any errors during the ETL process.
- For API errors, verify the API endpoints and check for any changes in the API documentation.