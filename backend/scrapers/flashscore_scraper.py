import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from loguru import logger
from .base_scraper import BaseScraper
from models.data_models import Match, Team, MatchStatus, OddsData, Statistics

class FlashScoreScraper(BaseScraper):
    """Scraper for FlashScore website"""
    
    def __init__(self):
        super().__init__("FlashScore", "https://www.flashscore.com")
        self.api_base = "https://api.flashscore.com"
        
    def scrape_matches(self, league_id: str, date_from: datetime, date_to: datetime) -> List[Dict]:
        """Scrape matches for La Liga and Conference League"""
        try:
            # FlashScore uses a specific URL structure for leagues
            if league_id == 'ES1':  # La Liga
                url = f"{self.base_url}/football/spain/la-liga/"
            elif 'conference' in league_id.lower():  # Conference League
                url = f"{self.base_url}/football/europe/uefa-conference-league/"
            else:
                url = f"{self.base_url}/football/"
            
            # For specific dates, we need to modify the URL
            if date_from.date() == datetime.now().date():
                url += "today/"
            elif date_from.date() == (datetime.now() + timedelta(days=1)).date():
                url += "tomorrow/"
            else:
                # For other dates, we need to use the calendar view
                date_str = date_from.strftime("%Y-%m-%d")
                url += f"fixtures/{date_str}/"
            
            response = self._make_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            matches = []
            
            # Find match containers - try multiple selectors
            match_containers = soup.find_all('div', class_='event__match')
            if not match_containers:
                match_containers = soup.find_all('div', class_='event__match--static')
            if not match_containers:
                match_containers = soup.find_all('div', class_='event__match--scheduled')
            
            for container in match_containers:
                try:
                    match_data = self._parse_match_container(container)
                    if match_data:
                        matches.append(match_data)
                except Exception as e:
                    logger.error(f"Error parsing match container: {e}")
                    continue
            
            logger.info(f"Scraped {len(matches)} matches from FlashScore")
            return matches
            
        except Exception as e:
            logger.error(f"Error scraping matches from FlashScore: {e}")
            return []
    
    def _parse_match_container(self, container) -> Optional[Dict]:
        """Parse individual match container"""
        try:
            # Extract match ID
            match_id = container.get('id', '').replace('g_1_', '')
            
            # Extract teams
            home_team_elem = container.find('div', class_='event__participant--home')
            away_team_elem = container.find('div', class_='event__participant--away')
            
            if not home_team_elem or not away_team_elem:
                return None
            
            home_team = home_team_elem.get_text(strip=True)
            away_team = away_team_elem.get_text(strip=True)
            
            # Extract score
            score_elem = container.find('div', class_='event__score')
            home_score = None
            away_score = None
            
            if score_elem:
                score_text = score_elem.get_text(strip=True)
                if ':' in score_text:
                    scores = score_text.split(':')
                    if len(scores) == 2:
                        home_score = int(scores[0]) if scores[0].isdigit() else None
                        away_score = int(scores[1]) if scores[1].isdigit() else None
            
            # Extract time/status
            time_elem = container.find('div', class_='event__time')
            status = MatchStatus.SCHEDULED
            match_time = None
            
            if time_elem:
                time_text = time_elem.get_text(strip=True)
                if 'FT' in time_text:
                    status = MatchStatus.FINISHED
                elif 'LIVE' in time_text:
                    status = MatchStatus.LIVE
                elif 'HT' in time_text:
                    status = MatchStatus.LIVE
                else:
                    # Try to parse time
                    try:
                        match_time = datetime.strptime(time_text, '%H:%M')
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
                'competition': 'La Liga',
                'season': '2024/2025'
            }
            
        except Exception as e:
            logger.error(f"Error parsing match container: {e}")
            return None
    
    def scrape_team_stats(self, team_id: str) -> Dict:
        """Scrape team statistics"""
        try:
            # FlashScore team URL structure
            url = f"{self.base_url}/team/{team_id}/"
            response = self._make_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            stats = {}
            
            # Extract form (last 5 matches)
            form_container = soup.find('div', class_='form')
            if form_container:
                form_matches = form_container.find_all('div', class_='form__item')
                form = []
                for match in form_matches:
                    result = match.get('class', [''])[-1]
                    if 'win' in result:
                        form.append('W')
                    elif 'draw' in result:
                        form.append('D')
                    elif 'loss' in result:
                        form.append('L')
                stats['form'] = form
            
            # Extract goals statistics
            goals_container = soup.find('div', class_='stat__row')
            if goals_container:
                goals_text = goals_container.get_text()
                # Parse goals scored and conceded
                goals_match = re.search(r'(\d+):(\d+)', goals_text)
                if goals_match:
                    stats['goals_scored'] = int(goals_match.group(1))
                    stats['goals_conceded'] = int(goals_match.group(2))
            
            # Extract other statistics
            stat_rows = soup.find_all('div', class_='stat__row')
            for row in stat_rows:
                label_elem = row.find('div', class_='stat__label')
                value_elem = row.find('div', class_='stat__value')
                
                if label_elem and value_elem:
                    label = label_elem.get_text(strip=True).lower().replace(' ', '_')
                    value = value_elem.get_text(strip=True)
                    
                    # Try to convert to number if possible
                    try:
                        if '.' in value:
                            stats[label] = float(value)
                        else:
                            stats[label] = int(value)
                    except:
                        stats[label] = value
            
            logger.info(f"Scraped stats for team {team_id}")
            return stats
            
        except Exception as e:
            logger.error(f"Error scraping team stats from FlashScore: {e}")
            return {}
    
    def scrape_h2h(self, team1_id: str, team2_id: str) -> Dict:
        """Scrape head-to-head statistics"""
        try:
            # FlashScore H2H URL structure
            url = f"{self.base_url}/h2h/{team1_id}/{team2_id}/"
            response = self._make_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            h2h_data = {
                'total_matches': 0,
                'team1_wins': 0,
                'team2_wins': 0,
                'draws': 0,
                'team1_goals': 0,
                'team2_goals': 0,
                'last_5_matches': []
            }
            
            # Find H2H matches
            matches = soup.find_all('div', class_='h2h__row')
            
            for match in matches:
                try:
                    # Extract match data
                    teams_elem = match.find('div', class_='h2h__teams')
                    score_elem = match.find('div', class_='h2h__score')
                    date_elem = match.find('div', class_='h2h__date')
                    
                    if teams_elem and score_elem:
                        teams_text = teams_elem.get_text(strip=True)
                        score_text = score_elem.get_text(strip=True)
                        
                        # Parse teams and score
                        if ' - ' in teams_text and ':' in score_text:
                            team1, team2 = teams_text.split(' - ')
                            score1, score2 = map(int, score_text.split(':'))
                            
                            h2h_data['total_matches'] += 1
                            h2h_data['team1_goals'] += score1
                            h2h_data['team2_goals'] += score2
                            
                            if score1 > score2:
                                h2h_data['team1_wins'] += 1
                            elif score2 > score1:
                                h2h_data['team2_wins'] += 1
                            else:
                                h2h_data['draws'] += 1
                            
                            # Add to last 5 matches
                            if len(h2h_data['last_5_matches']) < 5:
                                match_data = {
                                    'team1': team1,
                                    'team2': team2,
                                    'score1': score1,
                                    'score2': score2,
                                    'date': date_elem.get_text(strip=True) if date_elem else ''
                                }
                                h2h_data['last_5_matches'].append(match_data)
                
                except Exception as e:
                    logger.error(f"Error parsing H2H match: {e}")
                    continue
            
            logger.info(f"Scraped H2H data for {team1_id} vs {team2_id}")
            return h2h_data
            
        except Exception as e:
            logger.error(f"Error scraping H2H from FlashScore: {e}")
            return {}
    
    def scrape_odds(self, match_id: str) -> Dict:
        """Scrape odds for a match"""
        try:
            # FlashScore odds URL structure
            url = f"{self.base_url}/match/{match_id}/odds/"
            response = self._make_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
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
            
            # Find odds tables
            odds_tables = soup.find_all('div', class_='odds__table')
            
            for table in odds_tables:
                try:
                    # Extract bookmaker name
                    bookmaker_elem = table.find('div', class_='odds__bookmaker')
                    if not bookmaker_elem:
                        continue
                    
                    bookmaker = bookmaker_elem.get_text(strip=True)
                    
                    # Extract odds
                    odds_rows = table.find_all('div', class_='odds__row')
                    bookmaker_odds = {}
                    
                    for row in odds_rows:
                        label_elem = row.find('div', class_='odds__label')
                        value_elem = row.find('div', class_='odds__value')
                        
                        if label_elem and value_elem:
                            label = label_elem.get_text(strip=True).lower().replace(' ', '_')
                            value = value_elem.get_text(strip=True)
                            
                            try:
                                bookmaker_odds[label] = float(value)
                            except:
                                continue
                    
                    odds_data['bookmakers'][bookmaker] = bookmaker_odds
                    
                    # Use first bookmaker for main odds
                    if not odds_data['home_win'] and 'home_win' in bookmaker_odds:
                        odds_data['home_win'] = bookmaker_odds['home_win']
                        odds_data['draw'] = bookmaker_odds.get('draw')
                        odds_data['away_win'] = bookmaker_odds.get('away_win')
                
                except Exception as e:
                    logger.error(f"Error parsing odds table: {e}")
                    continue
            
            logger.info(f"Scraped odds for match {match_id}")
            return odds_data
            
        except Exception as e:
            logger.error(f"Error scraping odds from FlashScore: {e}")
            return {}
    
    def scrape_live_match(self, match_id: str) -> Dict:
        """Scrape live match data"""
        try:
            # FlashScore live match URL
            url = f"{self.base_url}/match/{match_id}/"
            response = self._make_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            live_data = {
                'minute': None,
                'home_score': None,
                'away_score': None,
                'events': [],
                'statistics': {}
            }
            
            # Extract current score and minute
            score_elem = soup.find('div', class_='event__score')
            if score_elem:
                score_text = score_elem.get_text(strip=True)
                if ':' in score_text:
                    scores = score_text.split(':')
                    if len(scores) == 2:
                        live_data['home_score'] = int(scores[0]) if scores[0].isdigit() else None
                        live_data['away_score'] = int(scores[1]) if scores[1].isdigit() else None
            
            # Extract minute
            minute_elem = soup.find('div', class_='event__time')
            if minute_elem:
                minute_text = minute_elem.get_text(strip=True)
                if "'" in minute_text:
                    try:
                        live_data['minute'] = int(minute_text.replace("'", ""))
                    except:
                        pass
            
            # Extract match events
            events_container = soup.find('div', class_='event__events')
            if events_container:
                events = events_container.find_all('div', class_='event__event')
                for event in events:
                    try:
                        event_text = event.get_text(strip=True)
                        live_data['events'].append(event_text)
                    except:
                        continue
            
            logger.info(f"Scraped live data for match {match_id}")
            return live_data
            
        except Exception as e:
            logger.error(f"Error scraping live match from FlashScore: {e}")
            return {}
