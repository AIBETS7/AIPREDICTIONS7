import requests
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from loguru import logger
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class LaLigaScraper(BaseScraper):
    """Scraper for official La Liga website"""
    
    def __init__(self):
        super().__init__("La Liga Official", "https://www.laliga.com")
        self.api_base = "https://www.laliga.com/api"
        
    def scrape_matches(self, league_id: str, date_from: datetime, date_to: datetime) -> List[Dict]:
        """Scrape matches from La Liga official website"""
        matches = []
        
        try:
            # La Liga website uses a different API structure
            # We'll scrape the calendar page for upcoming matches
            calendar_url = f"{self.base_url}/en-GB/calendar"
            
            response = self._make_request(calendar_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find match containers
            match_containers = soup.find_all('div', class_=re.compile(r'match|fixture'))
            
            for container in match_containers:
                try:
                    match_data = self._parse_match_container(container)
                    if match_data and self._is_match_in_date_range(match_data, date_from, date_to):
                        matches.append(match_data)
                except Exception as e:
                    logger.error(f"Error parsing match container: {e}")
                    continue
            
            logger.info(f"Scraped {len(matches)} matches from La Liga official website")
            
        except Exception as e:
            logger.error(f"Error scraping La Liga matches: {e}")
        
        return matches
    
    def _parse_match_container(self, container) -> Optional[Dict]:
        """Parse individual match container"""
        try:
            # Extract match date
            date_elem = container.find('time') or container.find(class_=re.compile(r'date|time'))
            match_date = None
            if date_elem:
                date_str = date_elem.get('datetime') or date_elem.text.strip()
                match_date = self._parse_date(date_str)
            
            # Extract teams
            team_elems = container.find_all(class_=re.compile(r'team|club'))
            home_team = away_team = None
            if len(team_elems) >= 2:
                home_team = team_elems[0].text.strip()
                away_team = team_elems[1].text.strip()
            
            # Extract match status
            status_elem = container.find(class_=re.compile(r'status|state'))
            status = 'scheduled'
            if status_elem:
                status_text = status_elem.text.strip().lower()
                if 'live' in status_text:
                    status = 'live'
                elif 'finished' in status_text or 'final' in status_text:
                    status = 'finished'
                elif 'postponed' in status_text:
                    status = 'postponed'
            
            # Extract score if available
            score_elem = container.find(class_=re.compile(r'score|result'))
            home_score = away_score = None
            if score_elem:
                score_text = score_elem.text.strip()
                score_match = re.search(r'(\d+)\s*-\s*(\d+)', score_text)
                if score_match:
                    home_score = int(score_match.group(1))
                    away_score = int(score_match.group(2))
            
            if home_team and away_team and match_date:
                return {
                    'id': f"laliga_{home_team}_{away_team}_{match_date.strftime('%Y%m%d')}",
                    'home_team': home_team,
                    'away_team': away_team,
                    'date': match_date.isoformat(),
                    'status': status,
                    'home_score': home_score,
                    'away_score': away_score,
                    'competition': 'La Liga',
                    'source': 'laliga_official',
                    'league_id': 'ES1'
                }
            
        except Exception as e:
            logger.error(f"Error parsing match container: {e}")
        
        return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string from La Liga website"""
        try:
            # Try different date formats
            formats = [
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%d/%m/%Y %H:%M',
                '%Y-%m-%d',
                '%d/%m/%Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str.strip(), fmt)
                except ValueError:
                    continue
            
            # If no format works, try to extract with regex
            date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
            if date_match:
                year, month, day = date_match.groups()
                return datetime(int(year), int(month), int(day))
            
        except Exception as e:
            logger.error(f"Error parsing date '{date_str}': {e}")
        
        return None
    
    def _is_match_in_date_range(self, match_data: Dict, date_from: datetime, date_to: datetime) -> bool:
        """Check if match is within the specified date range"""
        try:
            match_date = datetime.fromisoformat(match_data['date'].replace('Z', '+00:00'))
            return date_from <= match_date <= date_to
        except:
            return False
    
    def scrape_team_stats(self, team_id: str) -> Dict:
        """Scrape team statistics from La Liga website"""
        try:
            # La Liga website has team pages with statistics
            team_url = f"{self.base_url}/en-GB/teams/{team_id}"
            
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
                'source': 'laliga_official'
            }
            
            # Extract table data
            table = soup.find('table', class_=re.compile(r'standings|table'))
            if table:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 8:
                        team_name_cell = cells[1].text.strip()
                        if team_id.lower() in team_name_cell.lower():
                            stats['position'] = int(cells[0].text.strip())
                            stats['points'] = int(cells[2].text.strip())
                            stats['matches_played'] = int(cells[3].text.strip())
                            stats['wins'] = int(cells[4].text.strip())
                            stats['draws'] = int(cells[5].text.strip())
                            stats['losses'] = int(cells[6].text.strip())
                            stats['goals_for'] = int(cells[7].text.strip())
                            stats['goals_against'] = int(cells[8].text.strip())
                            stats['goal_difference'] = stats['goals_for'] - stats['goals_against']
                            break
            
            return stats
            
        except Exception as e:
            logger.error(f"Error scraping team stats for {team_id}: {e}")
            return {}
    
    def scrape_h2h(self, team1_id: str, team2_id: str) -> Dict:
        """Scrape head-to-head statistics"""
        try:
            # La Liga website might have H2H data
            h2h_url = f"{self.base_url}/en-GB/head-to-head/{team1_id}-vs-{team2_id}"
            
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
                'source': 'laliga_official'
            }
            
            # Parse H2H data from the page
            # This would need to be customized based on the actual HTML structure
            
            return h2h_data
            
        except Exception as e:
            logger.error(f"Error scraping H2H for {team1_id} vs {team2_id}: {e}")
            return {}
    
    def scrape_odds(self, match_id: str) -> Dict:
        """Scrape odds data (La Liga official site doesn't provide odds)"""
        # La Liga official website doesn't provide betting odds
        return {
            'match_id': match_id,
            'source': 'laliga_official',
            'odds_available': False,
            'message': 'Odds not available on official La Liga website'
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
                live_url = f"{self.base_url}/en-GB/live"
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
            # Extract live match information
            live_data = {
                'status': 'live',
                'minute': None,
                'home_score': None,
                'away_score': None,
                'events': [],
                'source': 'laliga_official'
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