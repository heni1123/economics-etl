import pytest
from typing import Dict, Any

def calculate_gdp_growth_yoy(row: Dict[str, Any]) -> float:
    if 'gdp_usd_prev' not in row or row['gdp_usd_prev'] is None or row['gdp_usd_prev'] == 0:
        return 0.0
    return (row['gdp_usd'] - row['gdp_usd_prev']) / row['gdp_usd_prev'] * 100

def calculate_population_growth_yoy(row: Dict[str, Any]) -> float:
    if 'population_prev' not in row or row['population_prev'] is None or row['population_prev'] == 0:
        return 0.0
    return (row['population'] - row['population_prev']) / row['population_prev'] * 100

def categorize_economic_size(row: Dict[str, Any]) -> str:
    if row['gdp_billions'] < 100:
        return 'Small'
    elif row['gdp_billions'] < 1000:
        return 'Medium'
    elif row['gdp_billions'] < 5000:
        return 'Large'
    else:
        return 'Major'

def test_calculate_gdp_growth_yoy():
    assert calculate_gdp_growth_yoy({'gdp_usd': 2000, 'gdp_usd_prev': 1000}) == 100.0
    assert calculate_gdp_growth_yoy({'gdp_usd': 1500, 'gdp_usd_prev': 1000}) == 50.0
    assert calculate_gdp_growth_yoy({'gdp_usd': 1000, 'gdp_usd_prev': 0}) == 0.0
    assert calculate_gdp_growth_yoy({'gdp_usd': 1000}) == 0.0

def test_calculate_population_growth_yoy():
    assert calculate_population_growth_yoy({'population': 2000, 'population_prev': 1000}) == 100.0
    assert calculate_population_growth_yoy({'population': 1500, 'population_prev': 1000}) == 50.0
    assert calculate_population_growth_yoy({'population': 1000, 'population_prev': 0}) == 0.0
    assert calculate_population_growth_yoy({'population': 1000}) == 0.0

def test_categorize_economic_size():
    assert categorize_economic_size({'gdp_billions': 50}) == 'Small'
    assert categorize_economic_size({'gdp_billions': 500}) == 'Medium'
    assert categorize_economic_size({'gdp_billions': 3000}) == 'Large'
    assert categorize_economic_size({'gdp_billions': 6000}) == 'Major'