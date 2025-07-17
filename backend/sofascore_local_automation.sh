#!/bin/bash
set -e

# Activar entorno virtual si existe
if [ -d "../.venv" ]; then
  source ../.venv/bin/activate
fi

# Ejecutar el scraper de Sofascore
python3 sofascore_scraper.py

# Hacer git add, commit y push si hay cambios en sofascore_stats.json
git add data/sofascore_stats.json
if ! git diff --cached --quiet; then
  git commit -m "chore(data): actualización automática Sofascore stats"
  git push
else
  echo "No hay cambios para hacer push."
fi 