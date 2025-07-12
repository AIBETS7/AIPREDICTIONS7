import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from loguru import logger

class RealMatchesCollector:
    """Collect real football match data using API-Football"""
    
    def __init__(self):
        # You'll need to get a free API key from https://www.api-football.com/
        self.api_key = os.getenv('API_FOOTBALL_KEY', 'your_api_key_here')
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': self.api_key
        }
        
        # Competition IDs for Spanish football and major competitions
        self.competitions = {
            'la_liga': 140,  # La Liga
            'copa_del_rey': 143,  # Copa del Rey
            'champions_league': 2,  # UEFA Champions League
            'europa_league': 3,  # UEFA Europa League
            'premier_league': 39,  # English Premier League
            'bundesliga': 78,  # German Bundesliga
            'serie_a': 135,  # Italian Serie A
            'ligue_1': 61,  # French Ligue 1
            'mls': 253,  # Major League Soccer (currently active)
            'brasileirao': 71,  # Brazilian Serie A (currently active)
            'argentina_liga': 128,  # Argentine Primera Division (currently active)
            'mexico_liga': 262,  # Mexican Liga MX (currently active)
        }
    
    def get_todays_matches(self) -> List[Dict]:
        """Get today's matches from major competitions"""
        logger.info("Fetching today's matches from API-Football")
        
        today = datetime.now().strftime('%Y-%m-%d')
        all_matches = []
        
        for comp_name, comp_id in self.competitions.items():
            try:
                matches = self._get_matches_by_date(comp_id, today)
                for match in matches:
                    match['competition'] = comp_name.replace('_', ' ').title()
                    match['competition_id'] = comp_id
                all_matches.extend(matches)
                logger.info(f"Found {len(matches)} matches for {comp_name}")
                
            except Exception as e:
                logger.error(f"Error fetching {comp_name} matches: {e}")
                continue
        
        return all_matches
    
    def get_upcoming_matches(self, days_ahead: int = 14) -> List[Dict]:
        """Get upcoming matches for the next N days"""
        logger.info(f"Fetching upcoming matches for next {days_ahead} days")
        
        all_matches = []
        today = datetime.now()
        
        for i in range(days_ahead):
            date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
            
            for comp_name, comp_id in self.competitions.items():
                try:
                    matches = self._get_matches_by_date(comp_id, date)
                    for match in matches:
                        match['competition'] = comp_name.replace('_', ' ').title()
                        match['competition_id'] = comp_id
                    all_matches.extend(matches)
                    
                except Exception as e:
                    logger.error(f"Error fetching {comp_name} matches for {date}: {e}")
                    continue
        
        return all_matches
    
    def _get_matches_by_date(self, competition_id: int, date: str) -> List[Dict]:
        """Get matches for a specific competition and date"""
        url = f"{self.base_url}/fixtures"
        params = {
            'league': competition_id,
            'season': 2024,  # Current season
            'date': date
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('response'):
                matches = []
                for fixture in data['response']:
                    match = self._format_fixture(fixture)
                    if match:
                        matches.append(match)
                return matches
            else:
                logger.warning(f"No response data for competition {competition_id} on {date}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for competition {competition_id}: {e}")
            return []
    
    def _format_fixture(self, fixture: Dict) -> Dict:
        """Format API fixture data to our standard format"""
        try:
            fixture_data = fixture['fixture']
            teams_data = fixture['teams']
            goals_data = fixture['goals']
            league_data = fixture['league']
            
            # Get team names
            home_team = teams_data['home']['name']
            away_team = teams_data['away']['name']
            
            # Get match time
            match_time = fixture_data['date']
            match_datetime = datetime.fromisoformat(match_time.replace('Z', '+00:00'))
            
            # Determine match status
            status = fixture_data['status']['short']
            if status in ['NS', 'TBD']:
                match_status = 'scheduled'
            elif status in ['1H', '2H', 'HT', 'ET', 'P', 'BT']:
                match_status = 'live'
            elif status in ['FT', 'AET', 'PEN', 'FT_PEN']:
                match_status = 'finished'
            else:
                match_status = 'unknown'
            
            return {
                'id': str(fixture_data['id']),
                'home_team': home_team,
                'away_team': away_team,
                'match_time': match_datetime.isoformat(),
                'status': match_status,
                'competition': league_data['name'],
                'competition_id': league_data['id'],
                'venue': fixture_data.get('venue', {}).get('name', 'Unknown'),
                'referee': fixture_data.get('referee', 'Unknown'),
                'home_score': goals_data.get('home'),
                'away_score': goals_data.get('away'),
                'api_data': fixture  # Keep original API data for reference
            }
            
        except Exception as e:
            logger.error(f"Error formatting fixture: {e}")
            return None
    
    def get_team_stats(self, team_id: int) -> Dict:
        """Get team statistics"""
        url = f"{self.base_url}/teams/statistics"
        params = {
            'team': team_id,
            'league': 140,  # La Liga
            'season': 2024
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('response'):
                return data['response']
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching team stats: {e}")
            return {}
    
    def get_match_odds(self, fixture_id: int) -> Dict:
        """Get match odds (if available)"""
        url = f"{self.base_url}/odds"
        params = {
            'fixture': fixture_id
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('response'):
                return data['response']
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching match odds: {e}")
            return {}
    
    def get_h2h_data(self, team1_id: int, team2_id: int) -> Dict:
        """Get head-to-head data between two teams"""
        url = f"{self.base_url}/fixtures/headtohead"
        params = {
            'h2h': f"{team1_id}-{team2_id}",
            'last': 10  # Last 10 meetings
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('response'):
                return data['response']
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching H2H data: {e}")
            return {}

# Fallback data for when API is not available
def get_fallback_matches() -> List[Dict]:
    """Provide fallback match data when API is not available"""
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    
    return [
        {
            'id': 'fallback_1',
            'home_team': 'Real Madrid',
            'away_team': 'Barcelona',
            'match_time': tomorrow.replace(hour=21, minute=0, second=0, microsecond=0).isoformat(),
            'status': 'scheduled',
            'competition': 'La Liga',
            'competition_id': 140,
            'venue': 'Santiago Bernabéu',
            'referee': 'TBD',
            'home_score': None,
            'away_score': None,
            'api_data': {}
        },
        {
            'id': 'fallback_2',
            'home_team': 'Atlético Madrid',
            'away_team': 'Sevilla',
            'match_time': tomorrow.replace(hour=19, minute=30, second=0, microsecond=0).isoformat(),
            'status': 'scheduled',
            'competition': 'La Liga',
            'competition_id': 140,
            'venue': 'Metropolitano',
            'referee': 'TBD',
            'home_score': None,
            'away_score': None,
            'api_data': {}
        }
    ] 