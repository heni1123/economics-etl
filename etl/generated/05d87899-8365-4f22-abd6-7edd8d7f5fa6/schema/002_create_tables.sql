CREATE TABLE IF NOT EXISTS public.fact_economic_indicators (
    country_code VARCHAR(3) NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 1960 AND 2030),
    gdp_usd NUMERIC CHECK (gdp_usd >= 0),
    gdp_growth_yoy NUMERIC,
    population_growth_yoy NUMERIC,
    economic_size_category VARCHAR(50),
    PRIMARY KEY (country_code, year)
);

CREATE INDEX idx_fact_economic_indicators_timestamp ON public.fact_economic_indicators (year);
CREATE INDEX idx_fact_economic_indicators_country_code ON public.fact_economic_indicators (country_code);
CREATE INDEX idx_fact_economic_indicators_economic_size_category ON public.fact_economic_indicators (economic_size_category);