from .base_scraper import BaseScraper
from typing import List, Dict, Any
from loguru import logger
from bs4 import BeautifulSoup, Tag
import re

class TransfermarktScraper(BaseScraper):
    """Scraper para Transfermarkt: traspasos, valores de mercado y plantillas"""
    def __init__(self):
        super().__init__("Transfermarkt", "https://www.transfermarkt.com")

    def scrape_transfers(self, league_id: str = "ES1", season: str = "2024", limit: int = 20) -> List[Dict[str, Any]]:
        """Scrapea los traspasos recientes de LaLiga desde Transfermarkt"""
        url = f"https://www.transfermarkt.com/laliga/transfers/wettbewerb/{league_id}/plus/?saison_id={season}"
        logger.info(f"Scraping traspasos de {url}")
        try:
            response = self._make_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            transfers = []
            # Buscar la tabla de traspasos (puede haber varias, nos interesa la de 'Arrivals' y 'Departures')
            tables = soup.find_all('table', class_='items')
            for table in tables:
                # Determinar si es arrivals o departures
                heading = table.find_previous('div', class_='table-header')
                if heading and 'Arrivals' in heading.text:
                    transfer_type = 'arrival'
                elif heading and 'Departures' in heading.text:
                    transfer_type = 'departure'
                else:
                    continue
                rows = table.find('tbody').find_all('tr', recursive=False)
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) < 8:
                        continue
                    player = cols[0].get_text(strip=True)
                    age = cols[1].get_text(strip=True)
                    nationality = cols[2].find('img')['title'] if cols[2].find('img') else ''
                    position = cols[3].get_text(strip=True)
                    from_team = cols[5].get_text(strip=True) if transfer_type == 'arrival' else cols[4].get_text(strip=True)
                    to_team = cols[4].get_text(strip=True) if transfer_type == 'arrival' else cols[5].get_text(strip=True)
                    fee = cols[8].get_text(strip=True) if len(cols) > 8 else ''
                    transfers.append({
                        'player': player,
                        'age': age,
                        'nationality': nationality,
                        'position': position,
                        'from_team': from_team,
                        'to_team': to_team,
                        'fee': fee,
                        'type': transfer_type
                    })
                    if len(transfers) >= limit:
                        break
                if len(transfers) >= limit:
                    break
            logger.info(f"Scrapeados {len(transfers)} traspasos de LaLiga")
            return transfers[:limit]
        except Exception as e:
            logger.error(f"Error scraping traspasos Transfermarkt: {e}")
            return []

    def scrape_market_values(self, league_id: str = "ES1", season: str = "2024") -> List[Dict[str, Any]]:
        """Scrapea valores de mercado de equipos y jugadores de LaLiga desde Transfermarkt"""
        url = f"https://www.transfermarkt.com/laliga/startseite/wettbewerb/{league_id}/plus/?saison_id={season}"
        logger.info(f"Scraping valores de mercado de {url}")
        try:
            response = self._make_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            teams = []
            table = soup.find('table', class_='items')
            if not table:
                logger.warning("No se encontró la tabla de equipos en Transfermarkt")
                return []
            tbody = table.find('tbody')
            if not (tbody and isinstance(tbody, Tag)):
                logger.warning("No se encontró el tbody de la tabla de equipos en Transfermarkt")
                return []
            rows = [row for row in tbody.find_all('tr', recursive=False) if isinstance(row, Tag) and row.find_all('td')]
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 5:
                    continue
                # Equipo
                team_name = cols[1].get_text(strip=True)
                # Valor de mercado del equipo
                team_value = cols[-1].get_text(strip=True)
                # Enlace a la plantilla para scraping de jugadores
                team_link = cols[1].find('a')['href'] if cols[1].find('a') else None
                players = []
                if team_link:
                    team_url = f"https://www.transfermarkt.com{team_link}"
                    try:
                        team_resp = self._make_request(team_url)
                        team_soup = BeautifulSoup(team_resp.content, 'html.parser')
                        player_table = team_soup.find('table', class_='items')
                        if player_table:
                            pbody = player_table.find('tbody')
                            if not (pbody and isinstance(pbody, Tag)):
                                continue
                            player_rows = [prow for prow in pbody.find_all('tr', recursive=False) if isinstance(prow, Tag) and prow.find_all('td')]
                            for prow in player_rows:
                                pcols = prow.find_all('td')
                                if len(pcols) < 7:
                                    continue
                                player_name = pcols[1].get_text(strip=True)
                                position = pcols[4].get_text(strip=True)
                                age = pcols[5].get_text(strip=True)
                                nationality = pcols[2].find('img')['title'] if pcols[2].find('img') else ''
                                market_value = pcols[-1].get_text(strip=True)
                                players.append({
                                    'name': player_name,
                                    'position': position,
                                    'age': age,
                                    'nationality': nationality,
                                    'market_value': market_value
                                })
                    except Exception as e:
                        logger.warning(f"Error scraping plantilla de {team_name}: {e}")
                teams.append({
                    'team': team_name,
                    'team_value': team_value,
                    'players': players
                })
            logger.info(f"Scrapeados valores de mercado de {len(teams)} equipos de LaLiga")
            return teams
        except Exception as e:
            logger.error(f"Error scraping valores de mercado Transfermarkt: {e}")
            return []

    def scrape_squads(self, league_id: str = "ES1", season: str = "2024") -> List[Dict[str, Any]]:
        """Scrapea plantillas de equipos de LaLiga desde Transfermarkt"""
        from bs4 import BeautifulSoup, Tag
        url = f"https://www.transfermarkt.com/laliga/startseite/wettbewerb/{league_id}/plus/?saison_id={season}"
        logger.info(f"Scraping plantillas de {url}")
        try:
            response = self._make_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            squads = []
            table = soup.find('table', class_='items')
            if not table:
                logger.warning("No se encontró la tabla de equipos en Transfermarkt")
                return []
            tbody = table.find('tbody')
            if not (tbody and isinstance(tbody, Tag)):
                logger.warning("No se encontró el tbody de la tabla de equipos en Transfermarkt")
                return []
            rows = [row for row in tbody.find_all('tr', recursive=False) if isinstance(row, Tag) and row.find_all('td')]
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 5:
                    continue
                team_name = cols[1].get_text(strip=True)
                team_link = cols[1].find('a')['href'] if cols[1].find('a') else None
                players = []
                if team_link:
                    team_url = f"https://www.transfermarkt.com{team_link}"
                    try:
                        team_resp = self._make_request(team_url)
                        team_soup = BeautifulSoup(team_resp.content, 'html.parser')
                        player_table = team_soup.find('table', class_='items')
                        if player_table:
                            pbody = player_table.find('tbody')
                            if not (pbody and isinstance(pbody, Tag)):
                                continue
                            player_rows = [prow for prow in pbody.find_all('tr', recursive=False) if isinstance(prow, Tag) and prow.find_all('td')]
                            for prow in player_rows:
                                pcols = prow.find_all('td')
                                if len(pcols) < 7:
                                    continue
                                player_name = pcols[1].get_text(strip=True)
                                position = pcols[4].get_text(strip=True)
                                age = pcols[5].get_text(strip=True)
                                nationality = pcols[2].find('img')['title'] if pcols[2].find('img') else ''
                                market_value = pcols[-1].get_text(strip=True)
                                players.append({
                                    'name': player_name,
                                    'position': position,
                                    'age': age,
                                    'nationality': nationality,
                                    'market_value': market_value
                                })
                    except Exception as e:
                        logger.warning(f"Error scraping plantilla de {team_name}: {e}")
                squads.append({
                    'team': team_name,
                    'players': players
                })
            logger.info(f"Scrapeadas plantillas de {len(squads)} equipos de LaLiga")
            return squads
        except Exception as e:
            logger.error(f"Error scraping plantillas Transfermarkt: {e}")
            return []

    def scrape_matches(self, league_id: str, date_from, date_to) -> List[Dict]:
        """Stub: Transfermarkt no provee partidos directamente, devolver lista vacía"""
        return []

    def scrape_team_stats(self, team_id: str) -> Dict:
        """Stub: Implementar scraping real en el futuro"""
        return {}

    def scrape_h2h(self, team1_id: str, team2_id: str) -> Dict:
        """Stub: Implementar scraping real en el futuro"""
        return {}

    def scrape_odds(self, match_id: str) -> Dict:
        """Stub: Transfermarkt no provee cuotas, devolver dict vacío"""
        return {}

    def scrape_live_match(self, match_id: str) -> Dict:
        """Stub: Transfermarkt no provee datos en vivo, devolver dict vacío"""
        return {} 