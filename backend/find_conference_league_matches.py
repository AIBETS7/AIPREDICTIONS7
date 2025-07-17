#!/usr/bin/env python3
"""
Find Conference League matches for tomorrow using multiple strategies
"""

import os
import requests
import json
from datetime import datetime, timedelta
from loguru import logger
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper

class ConferenceLeagueFinder(BaseScraper):
    """Find Conference League matches using multiple strategies"""
    
    def __init__(self):
        super().__init__("ConferenceLeagueFinder", "https://www.google.com")
    
    def scrape_matches(self, league_id: str, date_from: datetime, date_to: datetime):
        """Required abstract method - not used here"""
        return []
    
    def scrape_team_stats(self, team_id: str):
        """Required abstract method - not used here"""
        return {}
    
    def scrape_h2h(self, team1_id: str, team2_id: str):
        """Required abstract method - not used here"""
        return {}
    
    def scrape_odds(self, match_id: str):
        """Required abstract method - not used here"""
        return {}
    
    def scrape_live_match(self, match_id: str):
        """Required abstract method - not used here"""
        return {}
    
    def find_matches_google(self):
        """Search Google for Conference League matches tomorrow"""
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')
        
        search_query = f"UEFA Conference League matches {tomorrow_str} schedule"
        url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        
        try:
            response = self._make_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for match information in search results
            matches = []
            
            # Search for common match patterns
            text_content = soup.get_text().lower()
            
            # Look for team names and times
            if 'conference league' in text_content:
                print(f"✅ Found Conference League mentions for {tomorrow_str}")
                
                # Extract potential match information
                search_results = soup.find_all('div', class_='g')
                for result in search_results:
                    title = result.find('h3')
                    snippet = result.find('div', class_='VwiC3b')
                    
                    if title and snippet:
                        title_text = title.get_text()
                        snippet_text = snippet.get_text()
                        
                        if 'conference' in title_text.lower() or 'conference' in snippet_text.lower():
                            print(f"Match info: {title_text}")
                            print(f"Snippet: {snippet_text}")
                            matches.append({
                                'source': 'google',
                                'title': title_text,
                                'snippet': snippet_text
                            })
            
            return matches
            
        except Exception as e:
            logger.error(f"Error searching Google: {e}")
            return []
    
    def find_matches_api_football(self):
        """Try to find matches using football-data.org API"""
        try:
            # Free API key (limited requests)
            api_key = "test"  # You can get a free key from football-data.org
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow_str = tomorrow.strftime('%Y-%m-%d')
            
            # Conference League competition ID (you may need to find the correct one)
            url = f"http://api.football-data.org/v2/competitions/2000/matches?dateFrom={tomorrow_str}&dateTo={tomorrow_str}"
            
            headers = {
                'X-Auth-Token': api_key
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                matches = []
                
                for match in data.get('matches', []):
                    matches.append({
                        'id': match.get('id'),
                        'home_team': match.get('homeTeam', {}).get('name'),
                        'away_team': match.get('awayTeam', {}).get('name'),
                        'time': match.get('utcDate'),
                        'status': match.get('status'),
                        'source': 'football-data.org'
                    })
                
                return matches
            else:
                print(f"API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error with football-data.org API: {e}")
            return []
    
    def find_matches_livescore(self):
        """Try to find matches using Livescore"""
        try:
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow_str = tomorrow.strftime('%Y-%m-%d')
            
            # Try different Livescore URLs
            urls = [
                f"https://www.livescore.com/football/tomorrow/",
                f"https://www.livescore.com/football/uefa-conference-league/",
                f"https://www.livescore.com/football/uefa-conference-league/tomorrow/"
            ]
            
            for url in urls:
                try:
                    response = self._make_request(url)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for match containers
                    match_containers = soup.find_all('div', class_='match-row')
                    if not match_containers:
                        match_containers = soup.find_all('div', class_='match')
                    
                    matches = []
                    for container in match_containers:
                        try:
                            home_team = container.find('div', class_='home-team')
                            away_team = container.find('div', class_='away-team')
                            time_elem = container.find('div', class_='time')
                            
                            if home_team and away_team:
                                matches.append({
                                    'home_team': home_team.get_text(strip=True),
                                    'away_team': away_team.get_text(strip=True),
                                    'time': time_elem.get_text(strip=True) if time_elem else None,
                                    'source': 'livescore'
                                })
                        except:
                            continue
                    
                    if matches:
                        return matches
                        
                except Exception as e:
                    logger.error(f"Error with Livescore URL {url}: {e}")
                    continue
            
            return []
            
        except Exception as e:
            logger.error(f"Error with Livescore: {e}")
            return []
    
    def find_matches_whoscored(self):
        """Try to find matches using WhoScored"""
        try:
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow_str = tomorrow.strftime('%Y-%m-%d')
            
            url = f"https://www.whoscored.com/Regions/252/Tournaments/2/Europe/UEFA-Champions-League"
            
            response = self._make_request(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for Conference League matches
            matches = []
            
            # Search for Conference League in the page
            text_content = soup.get_text()
            if 'conference league' in text_content.lower():
                print("Found Conference League mentions in WhoScored")
                
                # Try to extract match information
                match_elements = soup.find_all('div', class_='match-centre')
                for element in match_elements:
                    try:
                        teams = element.find_all('span', class_='team-name')
                        if len(teams) >= 2:
                            matches.append({
                                'home_team': teams[0].get_text(strip=True),
                                'away_team': teams[1].get_text(strip=True),
                                'source': 'whoscored'
                            })
                    except:
                        continue
            
            return matches
            
        except Exception as e:
            logger.error(f"Error with WhoScored: {e}")
            return []
    
    def create_sample_matches(self):
        """Create sample Conference League matches for testing"""
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')
        
        # Sample matches based on typical Conference League schedule
        sample_matches = [
            {
                'id': 'conf_001',
                'home_team': 'Fiorentina',
                'away_team': 'Molde',
                'time': f"{tomorrow_str} 21:00",
                'competition': 'UEFA Conference League',
                'status': 'scheduled',
                'source': 'sample'
            },
            {
                'id': 'conf_002', 
                'home_team': 'PAOK',
                'away_team': 'Dinamo Zagreb',
                'time': f"{tomorrow_str} 20:00",
                'competition': 'UEFA Conference League',
                'status': 'scheduled',
                'source': 'sample'
            },
            {
                'id': 'conf_003',
                'home_team': 'Slovan Bratislava',
                'away_team': 'Partizan',
                'time': f"{tomorrow_str} 19:00",
                'competition': 'UEFA Conference League',
                'status': 'scheduled',
                'source': 'sample'
            }
        ]
        
        return sample_matches

def main():
    """Main function to find Conference League matches"""
    finder = ConferenceLeagueFinder()
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    
    print(f"🔍 Searching for Conference League matches on {tomorrow_str}")
    print("=" * 60)
    
    all_matches = []
    
    # Try Google search
    print("\n1. Searching Google...")
    google_matches = finder.find_matches_google()
    all_matches.extend(google_matches)
    
    # Try football-data.org API
    print("\n2. Trying football-data.org API...")
    api_matches = finder.find_matches_api_football()
    all_matches.extend(api_matches)
    
    # Try Livescore
    print("\n3. Trying Livescore...")
    livescore_matches = finder.find_matches_livescore()
    all_matches.extend(livescore_matches)
    
    # Try WhoScored
    print("\n4. Trying WhoScored...")
    whoscored_matches = finder.find_matches_whoscored()
    all_matches.extend(whoscored_matches)
    
    # If no matches found, create sample matches
    if not all_matches:
        print("\n5. No matches found, creating sample matches for testing...")
        sample_matches = finder.create_sample_matches()
        all_matches.extend(sample_matches)
    
    # Save matches to file
    output_file = f"conference_league_matches_{tomorrow_str}.json"
    with open(output_file, 'w') as f:
        json.dump(all_matches, f, indent=2)
    
    print(f"\n✅ Found {len(all_matches)} matches:")
    for i, match in enumerate(all_matches, 1):
        print(f"{i}. {match.get('home_team', 'Unknown')} vs {match.get('away_team', 'Unknown')}")
        print(f"   Time: {match.get('time', 'TBD')}")
        print(f"   Source: {match.get('source', 'Unknown')}")
        print()
    
    print(f"📁 Matches saved to: {output_file}")
    
    return all_matches

if __name__ == "__main__":
    main() 