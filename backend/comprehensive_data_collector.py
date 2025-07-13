#!/usr/bin/env python3
"""
Comprehensive Data Collector
Scrapes data from multiple football websites for better AI evaluation
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

class ComprehensiveDataCollector:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def collect_from_whoscored(self):
        """Collect data from WhoScored"""
        logger.info("Collecting data from WhoScored...")
        try:
            # WhoScored API endpoints for various leagues
            leagues = [
                {'name': 'La Liga', 'id': 'spain/primera-division'},
                {'name': 'Premier League', 'id': 'england/premier-league'},
                {'name': 'Bundesliga', 'id': 'germany/bundesliga'},
                {'name': 'Serie A', 'id': 'italy/serie-a'},
                {'name': 'Ligue 1', 'id': 'france/ligue-1'},
                {'name': 'Ecuador LigaPro', 'id': 'ecuador/liga-pro'}
            ]
            
            for league in leagues:
                try:
                    url = f"https://www.whoscored.com/Regions/252/Tournaments/2/{league['id']}"
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract match data
                        matches = soup.find_all('div', class_='match-centre')
                        for match in matches:
                            self.process_whoscored_match(match, league['name'])
                            
                    time.sleep(random.uniform(1, 3))  # Be respectful
                    
                except Exception as e:
                    logger.error(f"Error collecting from WhoScored {league['name']}: {e}")
                    
        except Exception as e:
            logger.error(f"Error collecting from WhoScored: {e}")
    
    def collect_from_bdfutbol(self):
        """Collect data from BDFutbol"""
        logger.info("Collecting data from BDFutbol...")
        try:
            # BDFutbol has good Spanish football data
            leagues = [
                {'name': 'La Liga', 'url': 'https://www.bdfutbol.com/es/t/t.html'},
                {'name': 'Segunda', 'url': 'https://www.bdfutbol.com/es/t/t2.html'},
                {'name': 'Copa del Rey', 'url': 'https://www.bdfutbol.com/es/t/tc.html'}
            ]
            
            for league in leagues:
                try:
                    response = self.session.get(league['url'], timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract match data from tables
                        tables = soup.find_all('table')
                        for table in tables:
                            rows = table.find_all('tr')
                            for row in rows[1:]:  # Skip header
                                self.process_bdfutbol_match(row, league['name'])
                                
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.error(f"Error collecting from BDFutbol {league['name']}: {e}")
                    
        except Exception as e:
            logger.error(f"Error collecting from BDFutbol: {e}")
    
    def collect_from_soccerway(self):
        """Collect data from Soccerway"""
        logger.info("Collecting data from Soccerway...")
        try:
            # Soccerway has comprehensive international data
            leagues = [
                {'name': 'La Liga', 'url': 'https://int.soccerway.com/national/spain/primera-division/20232024/regular-season/r'},
                {'name': 'Premier League', 'url': 'https://int.soccerway.com/national/england/premier-league/20232024/regular-season/r'},
                {'name': 'Ecuador LigaPro', 'url': 'https://int.soccerway.com/national/ecuador/liga-pro/2024/regular-season/r'}
            ]
            
            for league in leagues:
                try:
                    response = self.session.get(league['url'], timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract match data
                        matches = soup.find_all('tr', class_='match')
                        for match in matches:
                            self.process_soccerway_match(match, league['name'])
                            
                    time.sleep(random.uniform(1, 3))
                    
                except Exception as e:
                    logger.error(f"Error collecting from Soccerway {league['name']}: {e}")
                    
        except Exception as e:
            logger.error(f"Error collecting from Soccerway: {e}")
    
    def collect_from_resultados_futbol(self):
        """Collect data from Resultados-Futbol"""
        logger.info("Collecting data from Resultados-Futbol...")
        try:
            # Resultados-Futbol has good Spanish and international data
            leagues = [
                {'name': 'La Liga', 'url': 'https://www.resultados-futbol.com/primera'},
                {'name': 'Ecuador LigaPro', 'url': 'https://www.resultados-futbol.com/ecuador/liga-pro'}
            ]
            
            for league in leagues:
                try:
                    response = self.session.get(league['url'], timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract match data
                        matches = soup.find_all('div', class_='match')
                        for match in matches:
                            self.process_resultados_match(match, league['name'])
                            
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.error(f"Error collecting from Resultados-Futbol {league['name']}: {e}")
                    
        except Exception as e:
            logger.error(f"Error collecting from Resultados-Futbol: {e}")
    
    def collect_from_footballdatabase(self):
        """Collect data from FootballDatabase"""
        logger.info("Collecting data from FootballDatabase...")
        try:
            # FootballDatabase has historical and current data
            leagues = [
                {'name': 'La Liga', 'url': 'https://footballdatabase.com/league-spain/primera-division'},
                {'name': 'Ecuador LigaPro', 'url': 'https://footballdatabase.com/league-ecuador/liga-pro'}
            ]
            
            for league in leagues:
                try:
                    response = self.session.get(league['url'], timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract match data
                        matches = soup.find_all('tr', class_='match')
                        for match in matches:
                            self.process_footballdatabase_match(match, league['name'])
                            
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.error(f"Error collecting from FootballDatabase {league['name']}: {e}")
                    
        except Exception as e:
            logger.error(f"Error collecting from FootballDatabase: {e}")
    
    def collect_from_fcstats(self):
        """Collect data from FCStats"""
        logger.info("Collecting data from FCStats...")
        try:
            # FCStats has detailed statistics
            leagues = [
                {'name': 'La Liga', 'url': 'https://fcstats.com/league/Spain/La_Liga'},
                {'name': 'Ecuador LigaPro', 'url': 'https://fcstats.com/league/Ecuador/LigaPro'}
            ]
            
            for league in leagues:
                try:
                    response = self.session.get(league['url'], timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract match data
                        matches = soup.find_all('div', class_='match')
                        for match in matches:
                            self.process_fcstats_match(match, league['name'])
                            
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.error(f"Error collecting from FCStats {league['name']}: {e}")
                    
        except Exception as e:
            logger.error(f"Error collecting from FCStats: {e}")
    
    def process_whoscored_match(self, match_element, league):
        """Process a match from WhoScored"""
        try:
            # Extract match data from WhoScored format
            home_team = match_element.find('span', class_='home-team').text.strip()
            away_team = match_element.find('span', class_='away-team').text.strip()
            score = match_element.find('span', class_='score').text.strip()
            
            # Parse score
            if '-' in score:
                home_score, away_score = map(int, score.split('-'))
            else:
                home_score = away_score = None
            
            # Extract date and time
            date_element = match_element.find('span', class_='date')
            match_date = date_element.text.strip() if date_element else None
            
            # Store in database
            self.store_match_data(home_team, away_team, home_score, away_score, 
                                match_date, league, 'whoscored')
            
        except Exception as e:
            logger.error(f"Error processing WhoScored match: {e}")
    
    def process_bdfutbol_match(self, row_element, league):
        """Process a match from BDFutbol"""
        try:
            cells = row_element.find_all('td')
            if len(cells) >= 4:
                home_team = cells[0].text.strip()
                away_team = cells[1].text.strip()
                score_text = cells[2].text.strip()
                
                # Parse score
                if '-' in score_text:
                    home_score, away_score = map(int, score_text.split('-'))
                else:
                    home_score = away_score = None
                
                match_date = cells[3].text.strip() if len(cells) > 3 else None
                
                # Store in database
                self.store_match_data(home_team, away_team, home_score, away_score, 
                                    match_date, league, 'bdfutbol')
                
        except Exception as e:
            logger.error(f"Error processing BDFutbol match: {e}")
    
    def process_soccerway_match(self, match_element, league):
        """Process a match from Soccerway"""
        try:
            # Extract match data from Soccerway format
            teams = match_element.find_all('td', class_='team')
            if len(teams) >= 2:
                home_team = teams[0].text.strip()
                away_team = teams[1].text.strip()
                
                score_element = match_element.find('td', class_='score')
                if score_element:
                    score_text = score_element.text.strip()
                    if '-' in score_text:
                        home_score, away_score = map(int, score_text.split('-'))
                    else:
                        home_score = away_score = None
                else:
                    home_score = away_score = None
                
                date_element = match_element.find('td', class_='date')
                match_date = date_element.text.strip() if date_element else None
                
                # Store in database
                self.store_match_data(home_team, away_team, home_score, away_score, 
                                    match_date, league, 'soccerway')
                
        except Exception as e:
            logger.error(f"Error processing Soccerway match: {e}")
    
    def process_resultados_match(self, match_element, league):
        """Process a match from Resultados-Futbol"""
        try:
            # Extract match data from Resultados-Futbol format
            home_team = match_element.find('span', class_='home').text.strip()
            away_team = match_element.find('span', class_='away').text.strip()
            
            score_element = match_element.find('span', class_='score')
            if score_element:
                score_text = score_element.text.strip()
                if '-' in score_text:
                    home_score, away_score = map(int, score_text.split('-'))
                else:
                    home_score = away_score = None
            else:
                home_score = away_score = None
            
            date_element = match_element.find('span', class_='date')
            match_date = date_element.text.strip() if date_element else None
            
            # Store in database
            self.store_match_data(home_team, away_team, home_score, away_score, 
                                match_date, league, 'resultados-futbol')
                
        except Exception as e:
            logger.error(f"Error processing Resultados-Futbol match: {e}")
    
    def process_footballdatabase_match(self, match_element, league):
        """Process a match from FootballDatabase"""
        try:
            # Extract match data from FootballDatabase format
            teams = match_element.find_all('td', class_='team')
            if len(teams) >= 2:
                home_team = teams[0].text.strip()
                away_team = teams[1].text.strip()
                
                score_element = match_element.find('td', class_='score')
                if score_element:
                    score_text = score_element.text.strip()
                    if '-' in score_text:
                        home_score, away_score = map(int, score_text.split('-'))
                    else:
                        home_score = away_score = None
                else:
                    home_score = away_score = None
                
                date_element = match_element.find('td', class_='date')
                match_date = date_element.text.strip() if date_element else None
                
                # Store in database
                self.store_match_data(home_team, away_team, home_score, away_score, 
                                    match_date, league, 'footballdatabase')
                
        except Exception as e:
            logger.error(f"Error processing FootballDatabase match: {e}")
    
    def process_fcstats_match(self, match_element, league):
        """Process a match from FCStats"""
        try:
            # Extract match data from FCStats format
            home_team = match_element.find('span', class_='home-team').text.strip()
            away_team = match_element.find('span', class_='away-team').text.strip()
            
            score_element = match_element.find('span', class_='score')
            if score_element:
                score_text = score_element.text.strip()
                if '-' in score_text:
                    home_score, away_score = map(int, score_text.split('-'))
                else:
                    home_score = away_score = None
            else:
                home_score = away_score = None
            
            date_element = match_element.find('span', class_='date')
            match_date = date_element.text.strip() if date_element else None
            
            # Store in database
            self.store_match_data(home_team, away_team, home_score, away_score, 
                                match_date, league, 'fcstats')
                
        except Exception as e:
            logger.error(f"Error processing FCStats match: {e}")
    
    def store_match_data(self, home_team, away_team, home_score, away_score, 
                        match_date, league, source):
        """Store match data in the database"""
        try:
            with self.engine.connect() as conn:
                # Check if match already exists
                result = conn.execute(text("""
                    SELECT id FROM comprehensive_matches 
                    WHERE home_team = :home_team AND away_team = :away_team 
                    AND match_date = :match_date AND league = :league
                """), {
                    'home_team': home_team,
                    'away_team': away_team,
                    'match_date': match_date,
                    'league': league
                })
                
                if result.fetchone():
                    # Update existing match
                    conn.execute(text("""
                        UPDATE comprehensive_matches 
                        SET home_score = :home_score, away_score = :away_score,
                            source = :source, updated_at = NOW()
                        WHERE home_team = :home_team AND away_team = :away_team 
                        AND match_date = :match_date AND league = :league
                    """), {
                        'home_score': home_score,
                        'away_score': away_score,
                        'source': source,
                        'home_team': home_team,
                        'away_team': away_team,
                        'match_date': match_date,
                        'league': league
                    })
                else:
                    # Insert new match
                    conn.execute(text("""
                        INSERT INTO comprehensive_matches 
                        (home_team, away_team, home_score, away_score, match_date, 
                         league, source, created_at, updated_at)
                        VALUES (:home_team, :away_team, :home_score, :away_score, 
                                :match_date, :league, :source, NOW(), NOW())
                    """), {
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_score': home_score,
                        'away_score': away_score,
                        'match_date': match_date,
                        'league': league,
                        'source': source
                    })
                
                logger.info(f"Stored match: {home_team} vs {away_team} ({league}) from {source}")
                
        except Exception as e:
            logger.error(f"Error storing match data: {e}")
    
    def create_comprehensive_matches_table(self):
        """Create the comprehensive_matches table if it doesn't exist"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS comprehensive_matches (
                        id SERIAL PRIMARY KEY,
                        home_team VARCHAR(255) NOT NULL,
                        away_team VARCHAR(255) NOT NULL,
                        home_score INTEGER,
                        away_score INTEGER,
                        match_date VARCHAR(100),
                        league VARCHAR(255) NOT NULL,
                        source VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """))
                
                # Create index for better performance
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_comprehensive_matches_teams 
                    ON comprehensive_matches(home_team, away_team)
                """))
                
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_comprehensive_matches_league 
                    ON comprehensive_matches(league)
                """))
                
                logger.info("Comprehensive matches table created/verified")
                
        except Exception as e:
            logger.error(f"Error creating comprehensive_matches table: {e}")
    
    def run_comprehensive_collection(self):
        """Run the complete data collection from all sources"""
        logger.info("Starting comprehensive data collection...")
        
        # Create table if needed
        self.create_comprehensive_matches_table()
        
        # Collect from all sources
        self.collect_from_whoscored()
        self.collect_from_bdfutbol()
        self.collect_from_soccerway()
        self.collect_from_resultados_futbol()
        self.collect_from_footballdatabase()
        self.collect_from_fcstats()
        
        logger.info("Comprehensive data collection completed!")

def main():
    collector = ComprehensiveDataCollector()
    collector.run_comprehensive_collection()

if __name__ == "__main__":
    main() 