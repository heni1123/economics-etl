# Global Economic Indicators ETL — Daily Refresh

## Overview
Ce projet extrait et transforme des indicateurs économiques globaux depuis des APIs publiques gratuites. L'objectif est de fournir des données économiques comparatives entre pays et années pour la période 2020-2023. Les données incluent le PIB, la population, et les taux de change, permettant des analyses approfondies des tendances économiques mondiales.

## Architecture
L'architecture de l'ETL se compose de plusieurs étapes :
1. **Extraction** : Les données sont extraites de plusieurs APIs REST.
2. **Transformation** : Les données sont nettoyées et transformées pour répondre aux exigences de la base de données.
3. **Chargement** : Les données transformées sont chargées dans une base de données PostgreSQL.

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
1. Clone le dépôt GitHub : `git clone https://github.com/heni1123/economics-etl.git`
2. Installez les dépendances requises : `pip install -r requirements.txt`
3. Configurez les variables d'environnement :
   - `export GITHUB_TOKEN=<your_github_token>`
   - `export DB_PASSWORD=<your_database_password>`

## Configuration
Modifiez le fichier de configuration pour ajuster les paramètres de connexion à la base de données et les options d'extraction des données si nécessaire.

## Running
Pour exécuter le pipeline ETL, utilisez la commande suivante :
```
python etl_pipeline.py
```
Le pipeline peut être exécuté à la demande.

## Testing
Des tests unitaires sont inclus dans le répertoire `tests`. Pour exécuter les tests, utilisez :
```
pytest tests/
```

## Troubleshooting
- **Problèmes de connexion à l'API** : Vérifiez votre connexion Internet et assurez-vous que les URLs des APIs sont accessibles.
- **Erreurs de chargement dans PostgreSQL** : Assurez-vous que la base de données est en cours d'exécution et que les informations d'identification sont correctes.
- **Données manquantes** : Vérifiez les logs pour identifier les pays ou les années pour lesquels les données n'ont pas été extraites.