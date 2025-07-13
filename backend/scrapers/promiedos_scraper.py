import requests
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from loguru import logger
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class PromiedosScraper(BaseScraper):
    """Scraper for Promiedos website (covers Spanish football well)"""
    
    def __init__(self):
        super().__init__("Promiedos", "https://www.promiedos.com.ar")
        
    def scrape_matches(self, league_id: str, date_from: datetime, date_to: datetime) -> List[Dict]:
        """Scrape matches from Promiedos website"""
        matches = []
        
        try:
            # Promiedos has a specific URL structure for La Liga
            if league_id == 'ES1':  # La Liga
                league_url = f"{self.base_url}/league/laliga/bb"
            else:
                league_url = f"{self.base_url}/league/{league_id}"
            
            response = self._make_request(league_url)
            if not response:
                return matches
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for the JSON data in the script tag
            script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
            if script_tag:
                try:
                    json_data = json.loads(script_tag.string)
                    leagues = json_data.get('props', {}).get('pageProps', {}).get('data', {}).get('leagues', [])
                    
                    for league in leagues:
                        if league.get('id') == 'bb':  # La Liga ID
                            games = league.get('games', [])
                            
                            for game in games:
                                try:
                                    match_data = self._extract_match_from_json(game)
                                    if match_data and self._is_match_in_date_range(match_data, date_from, date_to):
                                        matches.append(match_data)
                                except Exception as e:
                                    logger.error(f"Error extracting match data: {e}")
                                    continue
                                    
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON data: {e}")
            
            logger.info(f"Scraped {len(matches)} matches from Promiedos")
            
        except Exception as e:
            logger.error(f"Error scraping Promiedos matches: {e}")
        
        return matches
    
    def _parse_match_row(self, row) -> Optional[Dict]:
        """Parse individual match row from table"""
        try:
            cells = row.find_all('td')
            if len(cells) < 4:  # Need at least date, home team, away team, score
                return None
            
            # Extract date
            date_cell = cells[0]
            date_text = date_cell.text.strip()
            match_date = self._parse_promiedos_date(date_text)
            
            if not match_date:
                return None
            
            # Extract teams
            home_team = cells[1].text.strip() if len(cells) > 1 else None
            away_team = cells[2].text.strip() if len(cells) > 2 else None
            
            if not home_team or not away_team:
                return None
            
            # Extract score and status
            score_cell = cells[3] if len(cells) > 3 else None
            home_score = away_score = None
            status = 'scheduled'
            
            if score_cell:
                score_text = score_cell.text.strip()
                if score_text and score_text != '-':
                    # Check if it's a score
                    score_match = re.search(r'(\d+)\s*-\s*(\d+)', score_text)
                    if score_match:
                        home_score = int(score_match.group(1))
                        away_score = int(score_match.group(2))
                        status = 'finished'
                    elif 'vs' in score_text.lower() or ':' in score_text:
                        # Scheduled match with time
                        status = 'scheduled'
                    elif 'postponed' in score_text.lower():
                        status = 'postponed'
                    elif 'cancelled' in score_text.lower():
                        status = 'cancelled'
            
            return {
                'id': f"promiedos_{home_team}_{away_team}_{match_date.strftime('%Y%m%d')}",
                'home_team': home_team,
                'away_team': away_team,
                'date': match_date.isoformat(),
                'status': status,
                'home_score': home_score,
                'away_score': away_score,
                'competition': 'La Liga',
                'source': 'promiedos',
                'league_id': 'ES1'
            }
            
        except Exception as e:
            logger.error(f"Error parsing match row: {e}")
        
        return None
    
    def _parse_promiedos_date(self, date_text: str) -> Optional[datetime]:
        """Parse date from Promiedos format"""
        try:
            # Promiedos uses formats like "15.08.2025" or "15/08/2025"
            date_formats = [
                '%d.%m.%Y',
                '%d/%m/%Y',
                '%d-%m-%Y',
                '%Y-%m-%d',
                '%d.%m.%y',
                '%d/%m/%y'
            ]
            
            # Clean the date text
            date_text = date_text.strip()
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_text, fmt)
                except ValueError:
                    continue
            
            # Try to extract with regex
            date_match = re.search(r'(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})', date_text)
            if date_match:
                day, month, year = date_match.groups()
                if len(year) == 2:
                    year = '20' + year
                return datetime(int(year), int(month), int(day))
            
        except Exception as e:
            logger.error(f"Error parsing Promiedos date '{date_text}': {e}")
        
        return None
    
    def _is_match_in_date_range(self, match_data: Dict, date_from: datetime, date_to: datetime) -> bool:
        """Check if match is within the specified date range"""
        try:
            match_date = datetime.fromisoformat(match_data['date'].replace('Z', '+00:00'))
            return date_from <= match_date <= date_to
        except:
            return False
    
    def scrape_team_stats(self, team_id: str) -> Dict:
        """Scrape team statistics from Promiedos"""
        try:
            # Promiedos has team pages with statistics
            team_url = f"{self.base_url}/team/{team_id}"
            
            response = self._make_request(team_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            stats = {
                'team_name': team_id,
                'position': None,
                'points': None,
                'matches_played': None,
                'wins': None,
                'draws': None,
                'losses': None,
                'goals_for': None,
                'goals_against': None,
                'goal_difference': None,
                'form': [],
                'source': 'promiedos'
            }
            
            # Find statistics table
            stats_table = soup.find('table', class_=re.compile(r'stats|standings|table'))
            if stats_table:
                rows = stats_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 8:
                        team_name_cell = cells[1].text.strip()
                        if team_id.lower() in team_name_cell.lower():
                            try:
                                stats['position'] = int(cells[0].text.strip())
                                stats['points'] = int(cells[2].text.strip())
                                stats['matches_played'] = int(cells[3].text.strip())
                                stats['wins'] = int(cells[4].text.strip())
                                stats['draws'] = int(cells[5].text.strip())
                                stats['losses'] = int(cells[6].text.strip())
                                stats['goals_for'] = int(cells[7].text.strip())
                                stats['goals_against'] = int(cells[8].text.strip())
                                stats['goal_difference'] = stats['goals_for'] - stats['goals_against']
                            except (ValueError, IndexError):
                                continue
                            break
            
            return stats
            
        except Exception as e:
            logger.error(f"Error scraping team stats for {team_id}: {e}")
            return {}
    
    def scrape_h2h(self, team1_id: str, team2_id: str) -> Dict:
        """Scrape head-to-head statistics"""
        try:
            # Promiedos might have H2H data
            h2h_url = f"{self.base_url}/h2h/{team1_id}-vs-{team2_id}"
            
            response = self._make_request(h2h_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            h2h_data = {
                'team1': team1_id,
                'team2': team2_id,
                'total_matches': 0,
                'team1_wins': 0,
                'team2_wins': 0,
                'draws': 0,
                'team1_goals': 0,
                'team2_goals': 0,
                'last_matches': [],
                'source': 'promiedos'
            }
            
            # Parse H2H data from the page
            h2h_table = soup.find('table', class_=re.compile(r'h2h|head-to-head'))
            if h2h_table:
                rows = h2h_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        try:
                            # Parse match result
                            result_text = cells[2].text.strip()
                            if result_text:
                                h2h_data['total_matches'] += 1
                                
                                # Determine winner
                                if '1' in result_text and '0' in result_text:
                                    if team1_id in cells[0].text:
                                        h2h_data['team1_wins'] += 1
                                    else:
                                        h2h_data['team2_wins'] += 1
                                elif 'X' in result_text or '-' in result_text:
                                    h2h_data['draws'] += 1
                        except:
                            continue
            
            return h2h_data
            
        except Exception as e:
            logger.error(f"Error scraping H2H for {team1_id} vs {team2_id}: {e}")
            return {}
    
    def scrape_odds(self, match_id: str) -> Dict:
        """Scrape odds data (Promiedos doesn't provide odds)"""
        return {
            'match_id': match_id,
            'source': 'promiedos',
            'odds_available': False,
            'message': 'Odds not available on Promiedos website'
        }
    
    def scrape_live_match(self, match_id: str) -> Dict:
        """Scrape live match data"""
        try:
            # Extract team names from match_id
            match_parts = match_id.split('_')
            if len(match_parts) >= 3:
                home_team = match_parts[1]
                away_team = match_parts[2]
                
                # Try to find live match data
                live_url = f"{self.base_url}/live"
                response = self._make_request(live_url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for the specific match
                match_containers = soup.find_all('div', class_=re.compile(r'match|fixture'))
                
                for container in match_containers:
                    team_elems = container.find_all(class_=re.compile(r'team|club'))
                    if len(team_elems) >= 2:
                        container_home = team_elems[0].text.strip()
                        container_away = team_elems[1].text.strip()
                        
                        if (home_team.lower() in container_home.lower() and 
                            away_team.lower() in container_away.lower()):
                            
                            return self._parse_live_match_data(container)
            
            return {'match_id': match_id, 'status': 'not_found'}
            
        except Exception as e:
            logger.error(f"Error scraping live match {match_id}: {e}")
            return {'match_id': match_id, 'status': 'error'}
    
    def _parse_live_match_data(self, container) -> Dict:
        """Parse live match data from container"""
        try:
            live_data = {
                'status': 'live',
                'minute': None,
                'home_score': None,
                'away_score': None,
                'events': [],
                'source': 'promiedos'
            }
            
            # Extract minute
            minute_elem = container.find(class_=re.compile(r'minute|time'))
            if minute_elem:
                minute_text = minute_elem.text.strip()
                minute_match = re.search(r'(\d+)', minute_text)
                if minute_match:
                    live_data['minute'] = int(minute_match.group(1))
            
            # Extract score
            score_elem = container.find(class_=re.compile(r'score|result'))
            if score_elem:
                score_text = score_elem.text.strip()
                score_match = re.search(r'(\d+)\s*-\s*(\d+)', score_text)
                if score_match:
                    live_data['home_score'] = int(score_match.group(1))
                    live_data['away_score'] = int(score_match.group(2))
            
            return live_data
            
        except Exception as e:
            logger.error(f"Error parsing live match data: {e}")
            return {'status': 'error'}
    
    def _extract_match_from_json(self, game_data: Dict) -> Optional[Dict]:
        """Extract match data from Promiedos JSON structure"""
        try:
            teams = game_data.get('teams', [])
            if len(teams) != 2:
                return None
                
            home_team = teams[0].get('name', '')
            away_team = teams[1].get('name', '')
            
            # Parse date
            start_time = game_data.get('start_time', '')
            if start_time:
                try:
                    # Format: "13-07-2025 14:15"
                    match_date = datetime.strptime(start_time, "%d-%m-%Y %H:%M")
                except:
                    match_date = datetime.now()
            else:
                match_date = datetime.now()
            
            # Get status
            status_info = game_data.get('status', {})
            status = status_info.get('name', 'scheduled')
            
            # Get odds
            odds_data = game_data.get('main_odds', {})
            odds_options = odds_data.get('options', [])
            
            odds = {}
            for option in odds_options:
                odds[option.get('name', '')] = option.get('value', 0)
            
            return {
                'id': game_data.get('id', ''),
                'home_team': home_team,
                'away_team': away_team,
                'date': match_date.isoformat(),
                'status': status.lower(),
                'odds': odds,
                'source': 'promiedos',
                'url_name': game_data.get('url_name', ''),
                'stage_round': game_data.get('stage_round_name', ''),
                'tv_networks': [net.get('name', '') for net in game_data.get('tv_networks', [])]
            }
            
        except Exception as e:
            logger.error(f"Error extracting match from JSON: {e}")
            return None 