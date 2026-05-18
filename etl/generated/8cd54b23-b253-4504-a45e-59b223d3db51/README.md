# Global Economic Indicators ETL — Daily Refresh

## Overview
Ce projet extrait et transforme des indicateurs économiques globaux depuis des APIs publiques gratuites. Les données sont utilisées pour l'analyse économique comparative entre pays et années (2020-2023). Le pipeline ETL est conçu pour être exécuté quotidiennement, avec un accent sur l'exactitude des calculs et la performance.

## Architecture
Le pipeline ETL suit une architecture en trois étapes : Extraction, Transformation et Chargement (ETL). Les données sont extraites de plusieurs APIs, transformées pour répondre aux règles métier, puis chargées dans une base de données PostgreSQL.

## Data Sources
- **World Bank GDP**: https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD
- **World Bank Population**: https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL
- **Exchange Rates API**: https://open.er-api.com/v6/latest/USD
- **REST Countries**: https://restcountries.com/v3.1/all

## Target Tables
- **fact_economic_indicators**
- **fact_exchange_rates**
- **dim_country**

## Installation
1. Clone le dépôt GitHub: `git clone https://github.com/heni1123/economics-etl.git`
2. Installez les dépendances requises: `pip install -r requirements.txt`
3. Configurez les variables d'environnement:
   - `export GITHUB_TOKEN=<your_github_token>`
   - `export DB_PASSWORD=<your_db_password>`

## Configuration
Les configurations spécifiques peuvent être ajustées dans le fichier `config.py`. Assurez-vous que les URLs des APIs et les paramètres de connexion à la base de données sont corrects.

## Running
Pour exécuter le pipeline ETL, utilisez la commande suivante:
```
python main.py
```
Le pipeline peut être exécuté à la demande, et il est recommandé de le faire à 02:00 UTC chaque jour.

## Testing
Des tests unitaires sont inclus dans le répertoire `tests`. Pour exécuter les tests, utilisez:
```
pytest tests/
```

## Troubleshooting
- **Problèmes de connexion API**: Vérifiez les URLs et assurez-vous que les APIs sont accessibles.
- **Erreurs de chargement dans PostgreSQL**: Vérifiez les logs pour des erreurs de validation des données.
- **Données manquantes**: Assurez-vous que les APIs fournissent des données pour les pays et les années requis.