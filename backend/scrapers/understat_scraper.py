import requests
from bs4 import BeautifulSoup, Tag
from loguru import logger
from typing import List, Dict, Any
import re
import json

class UnderstatScraper:
    """Scraper para Understat: xG, xGA, xPoints, tiros, conversiones, etc."""
    BASE_URL = "https://understat.com"

    def scrape_team_stats(self, league: str = "La_liga", season: str = "2023") -> List[Dict[str, Any]]:
        """Scrapea estadísticas avanzadas de equipos de una liga y temporada"""
        url = f"{self.BASE_URL}/league/{league}/{season}"
        logger.info(f"Scraping equipos de {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # Buscar el bloque de datos de equipos (JavaScript)
            script = soup.find('script', text=re.compile('teamsData'))
            if not script:
                logger.error("No se encontró el bloque de teamsData en la página de Understat")
                return []
            # Extraer el JSON de teamsData
            raw = re.search(r"teamsData\s+=\s+JSON.parse\('([^']+)'\)", script.string)
            if not raw:
                logger.error("No se pudo extraer el JSON de teamsData")
                return []
            json_data = raw.group(1).encode('utf-8').decode('unicode_escape')
            teams_data = json.loads(json_data)
            equipos = []
            for team_name, seasons in teams_data.items():
                if season not in seasons:
                    continue
                data = seasons[season]
                equipos.append({
                    'team': team_name,
                    'id': data.get('id'),
                    'matches': int(data.get('matches', 0)),
                    'wins': int(data.get('wins', 0)),
                    'draws': int(data.get('draws', 0)),
                    'loses': int(data.get('loses', 0)),
                    'goals': float(data.get('goals', 0)),
                    'xG': float(data.get('xG', 0)),
                    'xGA': float(data.get('xGA', 0)),
                    'xPoints': float(data.get('xPoints', 0)),
                    'shots': int(data.get('shots', 0)),
                    'shotsOnTarget': int(data.get('shotsOnTarget', 0)),
                    'deep': int(data.get('deep', 0)),
                    'ppda': float(data.get('ppda', {}).get('att', 0)),
                    'ppda_allowed': float(data.get('ppda_allowed', {}).get('att', 0)),
                    'fouls': int(data.get('fouls', 0)),
                    'corners': int(data.get('corners', 0)),
                    'yellow_cards': int(data.get('yellow_cards', 0)),
                    'red_cards': int(data.get('red_cards', 0)),
                    'result_form': data.get('form', ''),
                })
            logger.info(f"Scrapeados {len(equipos)} equipos de Understat para {league} {season}")
            return equipos
        except Exception as e:
            logger.error(f"Error scraping Understat: {e}")
            return []

    def scrape_match_stats(self, match_id: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/match/{match_id}"
        logger.info(f"Scraping partido de {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # Buscar el bloque de datos de partido (JavaScript)
            script = soup.find('script', text=re.compile('match_info'))
            if not (script and isinstance(script, Tag) and hasattr(script, 'string') and script.string):
                logger.error("No se encontró el bloque de match_info en la página de Understat")
                return {}
            # Extraer el JSON de match_info
            raw = re.search(r"match_info\s+=\s+JSON.parse\('([^']+)'\)", str(script.string or ''))
            if not raw:
                logger.error("No se pudo extraer el JSON de match_info")
                return {}
            json_data = raw.group(1).encode('utf-8').decode('unicode_escape')
            match_info = json.loads(json_data)[0]  # Es una lista con un dict
            # Buscar el bloque de datos de equipos (JavaScript)
            script_teams = soup.find('script', text=re.compile('teamsData'))
            teams_data = {}
            if script_teams and isinstance(script_teams, Tag) and hasattr(script_teams, 'string') and script_teams.string:
                raw_teams = re.search(r"teamsData\s+=\s+JSON.parse\('([^']+)'\)", str(script_teams.string or ''))
                if raw_teams:
                    json_teams = raw_teams.group(1).encode('utf-8').decode('unicode_escape')
                    teams_data = json.loads(json_teams)
            # Buscar el bloque de datos de eventos (shots)
            script_shots = soup.find('script', text=re.compile('shotsData'))
            shots_data = []
            if script_shots and isinstance(script_shots, Tag) and hasattr(script_shots, 'string') and script_shots.string:
                raw_shots = re.search(r"shotsData\s+=\s+JSON.parse\('([^']+)'\)", str(script_shots.string or ''))
                if raw_shots:
                    json_shots = raw_shots.group(1).encode('utf-8').decode('unicode_escape')
                    shots_data = json.loads(json_shots)
            # Resumir datos principales
            result = {
                'match_id': match_id,
                'date': match_info.get('date'),
                'home_team': match_info.get('h', {}).get('title'),
                'away_team': match_info.get('a', {}).get('title'),
                'home_goals': int(match_info.get('goals', {}).get('h', 0)),
                'away_goals': int(match_info.get('goals', {}).get('a', 0)),
                'home_xG': float(match_info.get('xG', {}).get('h', 0)),
                'away_xG': float(match_info.get('xG', {}).get('a', 0)),
                'home_shots': sum(1 for s in shots_data if s.get('h_a') == 'h'),
                'away_shots': sum(1 for s in shots_data if s.get('h_a') == 'a'),
                'home_shots_on_target': sum(1 for s in shots_data if s.get('h_a') == 'h' and s.get('result') == 'Goal'),
                'away_shots_on_target': sum(1 for s in shots_data if s.get('h_a') == 'a' and s.get('result') == 'Goal'),
                'teams_data': teams_data,
                'shots_data': shots_data,
            }
            return result
        except Exception as e:
            logger.error(f"Error scraping partido Understat: {e}")
            return {} 