#!/usr/bin/env python3
"""
Improved Data Collector
Focuses on current and upcoming matches with better parsing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import time
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from config.database import DATABASE_URL
from loguru import logger
import re
from bs4 import BeautifulSoup
import random

class ImprovedDataCollector:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def collect_current_matches(self):
        """Collect current and upcoming matches from multiple sources"""
        logger.info("Collecting current and upcoming matches...")
        
        # Create table if needed
        self.create_current_matches_table()
        
        # Collect from multiple sources
        self.collect_from_flashscore()
        self.collect_from_sofascore()
        self.collect_from_livescore()
        self.collect_from_espn()
        
        logger.info("Current matches collection completed!")
    
    def collect_from_flashscore(self):
        """Collect from FlashScore - good for current matches"""
        logger.info("Collecting from FlashScore...")
        try:
            # FlashScore has good current match data
            leagues = [
                {'name': 'La Liga', 'url': 'https://www.flashscore.com/football/spain/laliga/'},
                {'name': 'Premier League', 'url': 'https://www.flashscore.com/football/england/premier-league/'},
                {'name': 'Ecuador LigaPro', 'url': 'https://www.flashscore.com/football/ecuador/liga-pro/'}
            ]
            
            for league in leagues:
                try:
                    response = self.session.get(league['url'], timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for current matches
                        matches = soup.find_all('div', class_='event__match')
                        for match in matches:
                            self.process_flashscore_match(match, league['name'])
                            
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.error(f"Error collecting from FlashScore {league['name']}: {e}")
                    
        except Exception as e:
            logger.error(f"Error collecting from FlashScore: {e}")
    
    def collect_from_sofascore(self):
        """Collect from SofaScore - good for live matches"""
        logger.info("Collecting from SofaScore...")
        try:
            # SofaScore has good live match data
            leagues = [
                {'name': 'La Liga', 'url': 'https://www.sofascore.com/tournament/football/spain/laliga/7'},
                {'name': 'Premier League', 'url': 'https://www.sofascore.com/tournament/football/england/premier-league/17'},
                {'name': 'Ecuador LigaPro', 'url': 'https://www.sofascore.com/tournament/football/ecuador/liga-pro/12345'}
            ]
            
            for league in leagues:
                try:
                    response = self.session.get(league['url'], timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for current matches
                        matches = soup.find_all('div', class_='sc-fqkvVR')
                        for match in matches:
                            self.process_sofascore_match(match, league['name'])
                            
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.error(f"Error collecting from SofaScore {league['name']}: {e}")
                    
        except Exception as e:
            logger.error(f"Error collecting from SofaScore: {e}")
    
    def collect_from_livescore(self):
        """Collect from LiveScore - good for live scores"""
        logger.info("Collecting from LiveScore...")
        try:
            # LiveScore has good live data
            leagues = [
                {'name': 'La Liga', 'url': 'https://www.livescore.com/football/spain/laliga/'},
                {'name': 'Premier League', 'url': 'https://www.livescore.com/football/england/premier-league/'},
                {'name': 'Ecuador LigaPro', 'url': 'https://www.livescore.com/football/ecuador/liga-pro/'}
            ]
            
            for league in leagues:
                try:
                    response = self.session.get(league['url'], timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for current matches
                        matches = soup.find_all('div', class_='match-row')
                        for match in matches:
                            self.process_livescore_match(match, league['name'])
                            
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.error(f"Error collecting from LiveScore {league['name']}: {e}")
                    
        except Exception as e:
            logger.error(f"Error collecting from LiveScore: {e}")
    
    def collect_from_espn(self):
        """Collect from ESPN - good for comprehensive data"""
        logger.info("Collecting from ESPN...")
        try:
            # ESPN has good comprehensive data
            leagues = [
                {'name': 'La Liga', 'url': 'https://www.espn.com/soccer/league/_/name/esp.1'},
                {'name': 'Premier League', 'url': 'https://www.espn.com/soccer/league/_/name/eng.1'},
                {'name': 'Ecuador LigaPro', 'url': 'https://www.espn.com/soccer/league/_/name/ecu.1'}
            ]
            
            for league in leagues:
                try:
                    response = self.session.get(league['url'], timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for current matches
                        matches = soup.find_all('div', class_='gameModules')
                        for match in matches:
                            self.process_espn_match(match, league['name'])
                            
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.error(f"Error collecting from ESPN {league['name']}: {e}")
                    
        except Exception as e:
            logger.error(f"Error collecting from ESPN: {e}")
    
    def process_flashscore_match(self, match_element, league):
        """Process a match from FlashScore"""
        try:
            # Extract team names
            teams = match_element.find_all('div', class_='event__participant')
            if len(teams) >= 2:
                home_team = teams[0].text.strip()
                away_team = teams[1].text.strip()
                
                # Extract score
                score_element = match_element.find('div', class_='event__scores')
                if score_element:
                    score_text = score_element.text.strip()
                    if '-' in score_text:
                        scores = score_text.split('-')
                        if len(scores) == 2:
                            try:
                                home_score = int(scores[0].strip())
                                away_score = int(scores[1].strip())
                            except ValueError:
                                home_score = away_score = None
                        else:
                            home_score = away_score = None
                    else:
                        home_score = away_score = None
                else:
                    home_score = away_score = None
                
                # Extract date/time
                time_element = match_element.find('div', class_='event__time')
                match_time = time_element.text.strip() if time_element else None
                
                # Only store if it looks like a real match
                if self.is_valid_match(home_team, away_team):
                    self.store_current_match(home_team, away_team, home_score, away_score, 
                                           match_time, league, 'flashscore')
                
        except Exception as e:
            logger.error(f"Error processing FlashScore match: {e}")
    
    def process_sofascore_match(self, match_element, league):
        """Process a match from SofaScore"""
        try:
            # Extract team names
            teams = match_element.find_all('div', class_='sc-dcJsrY')
            if len(teams) >= 2:
                home_team = teams[0].text.strip()
                away_team = teams[1].text.strip()
                
                # Extract score
                score_element = match_element.find('div', class_='sc-gsFSXq')
                if score_element:
                    score_text = score_element.text.strip()
                    if '-' in score_text:
                        scores = score_text.split('-')
                        if len(scores) == 2:
                            try:
                                home_score = int(scores[0].strip())
                                away_score = int(scores[1].strip())
                            except ValueError:
                                home_score = away_score = None
                        else:
                            home_score = away_score = None
                    else:
                        home_score = away_score = None
                else:
                    home_score = away_score = None
                
                # Extract date/time
                time_element = match_element.find('div', class_='sc-hLBbgP')
                match_time = time_element.text.strip() if time_element else None
                
                # Only store if it looks like a real match
                if self.is_valid_match(home_team, away_team):
                    self.store_current_match(home_team, away_team, home_score, away_score, 
                                           match_time, league, 'sofascore')
                
        except Exception as e:
            logger.error(f"Error processing SofaScore match: {e}")
    
    def process_livescore_match(self, match_element, league):
        """Process a match from LiveScore"""
        try:
            # Extract team names
            teams = match_element.find_all('span', class_='team-name')
            if len(teams) >= 2:
                home_team = teams[0].text.strip()
                away_team = teams[1].text.strip()
                
                # Extract score
                score_element = match_element.find('span', class_='score')
                if score_element:
                    score_text = score_element.text.strip()
                    if '-' in score_text:
                        scores = score_text.split('-')
                        if len(scores) == 2:
                            try:
                                home_score = int(scores[0].strip())
                                away_score = int(scores[1].strip())
                            except ValueError:
                                home_score = away_score = None
                        else:
                            home_score = away_score = None
                    else:
                        home_score = away_score = None
                else:
                    home_score = away_score = None
                
                # Extract date/time
                time_element = match_element.find('span', class_='time')
                match_time = time_element.text.strip() if time_element else None
                
                # Only store if it looks like a real match
                if self.is_valid_match(home_team, away_team):
                    self.store_current_match(home_team, away_team, home_score, away_score, 
                                           match_time, league, 'livescore')
                
        except Exception as e:
            logger.error(f"Error processing LiveScore match: {e}")
    
    def process_espn_match(self, match_element, league):
        """Process a match from ESPN"""
        try:
            # Extract team names
            teams = match_element.find_all('span', class_='team-name')
            if len(teams) >= 2:
                home_team = teams[0].text.strip()
                away_team = teams[1].text.strip()
                
                # Extract score
                score_element = match_element.find('span', class_='score')
                if score_element:
                    score_text = score_element.text.strip()
                    if '-' in score_text:
                        scores = score_text.split('-')
                        if len(scores) == 2:
                            try:
                                home_score = int(scores[0].strip())
                                away_score = int(scores[1].strip())
                            except ValueError:
                                home_score = away_score = None
                        else:
                            home_score = away_score = None
                    else:
                        home_score = away_score = None
                else:
                    home_score = away_score = None
                
                # Extract date/time
                time_element = match_element.find('span', class_='time')
                match_time = time_element.text.strip() if time_element else None
                
                # Only store if it looks like a real match
                if self.is_valid_match(home_team, away_team):
                    self.store_current_match(home_team, away_team, home_score, away_score, 
                                           match_time, league, 'espn')
                
        except Exception as e:
            logger.error(f"Error processing ESPN match: {e}")
    
    def is_valid_match(self, home_team, away_team):
        """Check if this looks like a valid match (not season data)"""
        # Filter out season data and invalid team names
        invalid_patterns = [
            r'\d{4}-\d{2}',  # Year ranges like 2023-24
            r'\d{4}',        # Just years
            r'^\d+$',        # Just numbers
            r'IIIIIIIV',     # Roman numerals pattern
            r'^\d+\s+\d+$'   # Two numbers
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, home_team) or re.match(pattern, away_team):
                return False
        
        # Check for reasonable team name length
        if len(home_team) < 2 or len(away_team) < 2:
            return False
        
        if len(home_team) > 50 or len(away_team) > 50:
            return False
        
        return True
    
    def store_current_match(self, home_team, away_team, home_score, away_score, 
                           match_time, league, source):
        """Store current match data in the database"""
        try:
            with self.engine.connect() as conn:
                # Check if match already exists
                result = conn.execute(text("""
                    SELECT id FROM current_matches 
                    WHERE home_team = :home_team AND away_team = :away_team 
                    AND league = :league AND source = :source
                """), {
                    'home_team': home_team,
                    'away_team': away_team,
                    'league': league,
                    'source': source
                })
                
                if result.fetchone():
                    # Update existing match
                    conn.execute(text("""
                        UPDATE current_matches 
                        SET home_score = :home_score, away_score = :away_score,
                            match_time = :match_time, updated_at = NOW()
                        WHERE home_team = :home_team AND away_team = :away_team 
                        AND league = :league AND source = :source
                    """), {
                        'home_score': home_score,
                        'away_score': away_score,
                        'match_time': match_time,
                        'home_team': home_team,
                        'away_team': away_team,
                        'league': league,
                        'source': source
                    })
                else:
                    # Insert new match
                    conn.execute(text("""
                        INSERT INTO current_matches 
                        (home_team, away_team, home_score, away_score, match_time, 
                         league, source, created_at, updated_at)
                        VALUES (:home_team, :away_team, :home_score, :away_score, 
                                :match_time, :league, :source, NOW(), NOW())
                    """), {
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_score': home_score,
                        'away_score': away_score,
                        'match_time': match_time,
                        'league': league,
                        'source': source
                    })
                
                logger.info(f"Stored current match: {home_team} vs {away_team} ({league}) from {source}")
                
        except Exception as e:
            logger.error(f"Error storing current match data: {e}")
    
    def create_current_matches_table(self):
        """Create the current_matches table if it doesn't exist"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS current_matches (
                        id SERIAL PRIMARY KEY,
                        home_team VARCHAR(255) NOT NULL,
                        away_team VARCHAR(255) NOT NULL,
                        home_score INTEGER,
                        away_score INTEGER,
                        match_time VARCHAR(100),
                        league VARCHAR(255) NOT NULL,
                        source VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """))
                
                # Create index for better performance
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_current_matches_teams 
                    ON current_matches(home_team, away_team)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_current_matches_league 
                    ON current_matches(league)
                """))
                
                logger.info("Current matches table created/verified")
                
        except Exception as e:
            logger.error(f"Error creating current_matches table: {e}")

def main():
    collector = ImprovedDataCollector()
    collector.collect_current_matches()

if __name__ == "__main__":
    main() 