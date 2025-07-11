import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from loguru import logger
from .base_scraper import BaseScraper
from models.data_models import Match, Team, MatchStatus, OddsData, Statistics
from config.settings import BETSAPI_KEY

class BetsAPIScraper(BaseScraper):
    """Scraper for BetsAPI (uses their official API)"""
    
    def __init__(self):
        super().__init__("BetsAPI", "https://betsapi.com")
        self.api_key = BETSAPI_KEY
        self.api_base = "https://api.betsapi.com/v1"
        
    def _make_api_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request to BetsAPI"""
        if params is None:
            params = {}
        
        params['token'] = self.api_key
        
        try:
            response = self.session.get(
                f"{self.api_base}/{endpoint}",
                params=params,
                timeout=SCRAPING_CONFIG['timeout']
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"BetsAPI request failed: {e}")
            return {}
    
    def scrape_matches(self, league_id: str, date_from: datetime, date_to: datetime) -> List[Dict]:
        """Scrape matches using BetsAPI"""
        try:
            # Convert dates to required format
            date_from_str = date_from.strftime("%Y-%m-%d")
            date_to_str = date_to.strftime("%Y-%m-%d")
            
            # BetsAPI endpoint for events
            params = {
                'sport_id': 1,  # Football
                'league_id': league_id,
                'date_from': date_from_str,
                'date_to': date_to_str
            }
            
            response_data = self._make_api_request('events', params)
            
            matches = []
            
            if 'results' in response_data:
                for event in response_data['results']:
                    try:
                        match_data = self._parse_event_data(event)
                        if match_data:
                            matches.append(match_data)
                    except Exception as e:
                        logger.error(f"Error parsing event data: {e}")
                        continue
            
            logger.info(f"Scraped {len(matches)} matches from BetsAPI")
            return matches
            
        except Exception as e:
            logger.error(f"Error scraping matches from BetsAPI: {e}")
            return []
    
    def _parse_event_data(self, event: Dict) -> Optional[Dict]:
        """Parse event data from BetsAPI response"""
        try:
            match_id = str(event.get('id', ''))
            
            # Extract teams
            home_team = event.get('home', {}).get('name', '')
            away_team = event.get('away', {}).get('name', '')
            
            # Extract score
            home_score = event.get('ss', {}).get('home', None)
            away_score = event.get('ss', {}).get('away', None)
            
            # Convert scores to integers if they exist
            if home_score is not None:
                try:
                    home_score = int(home_score)
                except:
                    home_score = None
            
            if away_score is not None:
                try:
                    away_score = int(away_score)
                except:
                    away_score = None
            
            # Determine status
            status = MatchStatus.SCHEDULED
            time_status = event.get('time_status', '')
            
            if time_status == '1':
                status = MatchStatus.LIVE
            elif time_status == '3':
                status = MatchStatus.FINISHED
            elif time_status == '4':
                status = MatchStatus.CANCELLED
            elif time_status == '5':
                status = MatchStatus.POSTPONED
            
            # Extract time
            match_time = None
            time_str = event.get('time', '')
            if time_str:
                try:
                    # Parse Unix timestamp
                    match_time = datetime.fromtimestamp(int(time_str))
                except:
                    pass
            
            return {
                'id': match_id,
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'status': status,
                'time': match_time,
                'competition': event.get('league', {}).get('name', 'La Liga'),
                'season': '2024/2025'
            }
            
        except Exception as e:
            logger.error(f"Error parsing event data: {e}")
            return None
    
    def scrape_team_stats(self, team_id: str) -> Dict:
        """Scrape team statistics using BetsAPI"""
        try:
            # BetsAPI endpoint for team statistics
            params = {
                'team_id': team_id
            }
            
            response_data = self._make_api_request('team', params)
            
            stats = {}
            
            if 'results' in response_data:
                team_data = response_data['results']
                
                # Extract basic stats
                stats['name'] = team_data.get('name', '')
                stats['country'] = team_data.get('country', '')
                stats['league'] = team_data.get('league', '')
                
                # Extract form (if available)
                if 'form' in team_data:
                    stats['form'] = team_data['form']
                
                # Extract statistics
                if 'statistics' in team_data:
                    team_stats = team_data['statistics']
                    stats.update(team_stats)
            
            logger.info(f"Scraped stats for team {team_id}")
            return stats
            
        except Exception as e:
            logger.error(f"Error scraping team stats from BetsAPI: {e}")
            return {}
    
    def scrape_h2h(self, team1_id: str, team2_id: str) -> Dict:
        """Scrape head-to-head statistics using BetsAPI"""
        try:
            # BetsAPI endpoint for H2H
            params = {
                'team1_id': team1_id,
                'team2_id': team2_id
            }
            
            response_data = self._make_api_request('h2h', params)
            
            h2h_data = {
                'total_matches': 0,
                'team1_wins': 0,
                'team2_wins': 0,
                'draws': 0,
                'team1_goals': 0,
                'team2_goals': 0,
                'last_5_matches': []
            }
            
            if 'results' in response_data:
                matches = response_data['results']
                
                for match in matches:
                    try:
                        # Extract match data
                        team1_score = match.get('team1_score', 0)
                        team2_score = match.get('team2_score', 0)
                        date = match.get('date', '')
                        
                        h2h_data['total_matches'] += 1
                        h2h_data['team1_goals'] += team1_score
                        h2h_data['team2_goals'] += team2_score
                        
                        if team1_score > team2_score:
                            h2h_data['team1_wins'] += 1
                        elif team2_score > team1_score:
                            h2h_data['team2_wins'] += 1
                        else:
                            h2h_data['draws'] += 1
                        
                        # Add to last 5 matches
                        if len(h2h_data['last_5_matches']) < 5:
                            match_data = {
                                'team1_score': team1_score,
                                'team2_score': team2_score,
                                'date': date
                            }
                            h2h_data['last_5_matches'].append(match_data)
                    
                    except Exception as e:
                        logger.error(f"Error parsing H2H match: {e}")
                        continue
            
            logger.info(f"Scraped H2H data for {team1_id} vs {team2_id}")
            return h2h_data
            
        except Exception as e:
            logger.error(f"Error scraping H2H from BetsAPI: {e}")
            return {}
    
    def scrape_odds(self, match_id: str) -> Dict:
        """Scrape odds for a match using BetsAPI"""
        try:
            # BetsAPI endpoint for odds
            params = {
                'event_id': match_id
            }
            
            response_data = self._make_api_request('event/odds', params)
            
            odds_data = {
                'home_win': None,
                'draw': None,
                'away_win': None,
                'over_2_5': None,
                'under_2_5': None,
                'both_teams_score_yes': None,
                'both_teams_score_no': None,
                'bookmakers': {}
            }
            
            if 'results' in response_data:
                odds_results = response_data['results']
                
                for bookmaker in odds_results:
                    try:
                        bookmaker_name = bookmaker.get('name', '')
                        bookmaker_odds = {}
                        
                        # Extract different types of odds
                        for odd_type in bookmaker.get('odds', []):
                            odd_name = odd_type.get('name', '').lower().replace(' ', '_')
                            odd_value = odd_type.get('value')
                            
                            if odd_value:
                                try:
                                    bookmaker_odds[odd_name] = float(odd_value)
                                except:
                                    continue
                        
                        odds_data['bookmakers'][bookmaker_name] = bookmaker_odds
                        
                        # Use first bookmaker for main odds
                        if not odds_data['home_win'] and 'home_win' in bookmaker_odds:
                            odds_data['home_win'] = bookmaker_odds['home_win']
                            odds_data['draw'] = bookmaker_odds.get('draw')
                            odds_data['away_win'] = bookmaker_odds.get('away_win')
                    
                    except Exception as e:
                        logger.error(f"Error parsing bookmaker odds: {e}")
                        continue
            
            logger.info(f"Scraped odds for match {match_id}")
            return odds_data
            
        except Exception as e:
            logger.error(f"Error scraping odds from BetsAPI: {e}")
            return {}
    
    def scrape_live_match(self, match_id: str) -> Dict:
        """Scrape live match data using BetsAPI"""
        try:
            # BetsAPI endpoint for live events
            params = {
                'event_id': match_id
            }
            
            response_data = self._make_api_request('event/live', params)
            
            live_data = {
                'minute': None,
                'home_score': None,
                'away_score': None,
                'events': [],
                'statistics': {}
            }
            
            if 'results' in response_data:
                live_info = response_data['results']
                
                # Extract current score
                live_data['home_score'] = live_info.get('home_score')
                live_data['away_score'] = live_info.get('away_score')
                
                # Extract minute
                live_data['minute'] = live_info.get('minute')
                
                # Extract events
                if 'events' in live_info:
                    live_data['events'] = live_info['events']
                
                # Extract statistics
                if 'statistics' in live_info:
                    live_data['statistics'] = live_info['statistics']
            
            logger.info(f"Scraped live data for match {match_id}")
            return live_data
            
        except Exception as e:
            logger.error(f"Error scraping live match from BetsAPI: {e}")
            return {}
