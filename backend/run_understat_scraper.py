import os
import json
import logging
from datetime import datetime

from scrapers.understat_scraper import UnderstatScraper

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'understat')

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logging.info(f"Creada carpeta de datos: {DATA_DIR}")

def save_json(data, filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logging.info(f"Datos guardados en {path}")

def main():
    ensure_data_dir()
    scraper = UnderstatScraper()
    league = "La_liga"
    season = "2023"
    logging.info(f"Iniciando scraping de Understat (equipos) para {league} {season}...")
    teams_data = scraper.scrape_team_stats(league=league, season=season)
    save_json(teams_data, f"teams_{league}_{season}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    # Obtener partidos de los equipos (solo IDs únicos)
    match_ids = set()
    for team in teams_data:
        # Suponemos que hay un campo 'id' o similar, pero Understat no da todos los match_ids directamente
        # Aquí solo como ejemplo, normalmente necesitaríamos scrapear el calendario o lista de partidos
        pass  # TODO: scrapear lista de partidos por equipo/temporada si se implementa
    # Para demo, no scrapear partidos si no hay match_ids
    matches_data = []
    # for match_id in match_ids:
    #     match_stats = scraper.scrape_match_stats(match_id)
    #     matches_data.append(match_stats)
    save_json(matches_data, f"matches_{league}_{season}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    logging.info("Scraping de Understat finalizado correctamente.")

if __name__ == "__main__":
    main() 