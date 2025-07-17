#!/bin/bash
set -e

# Activar entorno virtual si existe
if [ -d "../.venv" ]; then
  source ../.venv/bin/activate
fi

# Ejecutar todos los scrapers principales
echo "Ejecutando sofascore_scraper.py..."
python3 sofascore_scraper.py || echo "Sofascore falló"

echo "Ejecutando flashscore_scraper.py..."
python3 flashscore_scraper.py || echo "Flashscore falló"

echo "Ejecutando betsapi_scraper.py..."
python3 -m scrapers.betsapi_scraper || echo "BetsAPI falló"

echo "Ejecutando promiedos_scraper.py..."
python3 -m scrapers.promiedos_scraper || echo "Promiedos falló"

echo "Ejecutando laliga_scraper.py..."
python3 -m scrapers.laliga_scraper || echo "LaLiga falló"

echo "Ejecutando transfermarkt_scraper.py..."
python3 -m scrapers.transfermarkt_scraper || echo "Transfermarkt falló"

echo "Ejecutando understat_scraper.py..."
python3 -m scrapers.understat_scraper || echo "Understat falló"

echo "Ejecutando odds_api_integration.py..."
python3 odds_api_integration.py || echo "Odds API falló"

echo "Ejecutando sportmonks_integration.py..."
python3 sportmonks_integration.py || echo "Sportmonks falló"

# Hacer git add, commit y push si hay cambios en los datos
git add data/*.json data/sofascore_stats.json
if ! git diff --cached --quiet; then
  git commit -m "chore(data): actualización automática de todos los scrapers principales"
  git push
else
  echo "No hay cambios para hacer push."
fi 