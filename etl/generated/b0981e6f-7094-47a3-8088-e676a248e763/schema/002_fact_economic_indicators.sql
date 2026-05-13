CREATE SCHEMA IF NOT EXISTS public;

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
    population_category VARCHAR(20),
    development_indicator VARCHAR(30),
    region VARCHAR(50),
    subregion VARCHAR(50),
    capital_city VARCHAR(100),
    area_km2 NUMERIC(12,2),
    population_density NUMERIC(10,2),
    load_timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (country_code, year)
);

CREATE TABLE IF NOT EXISTS public.fact_exchange_rates (
    base_currency VARCHAR(3) NOT NULL,
    target_currency VARCHAR(3) NOT NULL,
    exchange_rate NUMERIC(15,8) NOT NULL,
    rate_date DATE NOT NULL,
    rate_timestamp TIMESTAMPTZ NOT NULL,
    next_update_timestamp TIMESTAMPTZ,
    provider VARCHAR(50),
    load_timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (base_currency, target_currency, rate_date)
);

CREATE TABLE IF NOT EXISTS public.dim_country (
    country_code VARCHAR(3) NOT NULL,
    country_name_common VARCHAR(100),
    country_name_official VARCHAR(200),
    capital_city VARCHAR(100),
    region VARCHAR(50),
    subregion VARCHAR(50),
    area_km2 NUMERIC(12,2),
    primary_language VARCHAR(50),
    primary_currency VARCHAR(10),
    last_updated TIMESTAMPTZ,
    PRIMARY KEY (country_code)
);