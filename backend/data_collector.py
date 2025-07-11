import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from loguru import logger
from config.settings import DATA_SOURCES, LA_LIGA_CONFIG
from scrapers.flashscore_scraper import FlashScoreScraper
from scrapers.sofascore_scraper import SofaScoreScraper
from scrapers.betsapi_scraper import BetsAPIScraper
from models.data_models import Match, Team, H2HRecord, OddsData, Statistics

class DataCollector:
    """Main data collection orchestrator"""
    
    def __init__(self):
        self.scrapers = {
            'flashscore': FlashScoreScraper(),
            'sofascore': SofaScoreScraper(),
            'betsapi': BetsAPIScraper()
        }
        self.collected_data = {
            'matches': [],
            'teams': {},
            'h2h_records': {},
            'odds': {},
            'statistics': {}
        }
        self.last_update = {}
        
    def collect_all_data(self, days_back: int = 7, days_forward: int = 7) -> Dict:
        """Collect data from all sources"""
        logger.info("Starting data collection from all sources")
        
        date_from = datetime.now() - timedelta(days=days_back)
        date_to = datetime.now() + timedelta(days=days_forward)
        
        # Collect data from each source
        for source_name, source_config in DATA_SOURCES.items():
            if not source_config['enabled']:
                continue
                
            try:
                logger.info(f"Collecting data from {source_name}")
                self._collect_from_source(source_name, date_from, date_to)
                self.last_update[source_name] = datetime.now()
                
            except Exception as e:
                logger.error(f"Error collecting from {source_name}: {e}")
                continue
        
        # Merge and deduplicate data
        merged_data = self._merge_data()
        
        # Save to files
        self._save_data(merged_data)
        
        logger.info("Data collection completed")
        return merged_data
    
    def _collect_from_source(self, source_name: str, date_from: datetime, date_to: datetime):
        """Collect data from a specific source"""
        scraper = self.scrapers.get(source_name)
        if not scraper:
            logger.error(f"No scraper found for {source_name}")
            return
        
        # Collect matches
        matches = scraper.scrape_matches(LA_LIGA_CONFIG['league_id'], date_from, date_to)
        self.collected_data['matches'].extend(matches)
        
        # Collect team data for teams in matches
        teams_to_collect = set()
        for match in matches:
            teams_to_collect.add(match.get('home_team', ''))
            teams_to_collect.add(match.get('away_team', ''))
        
        for team_name in teams_to_collect:
            if team_name and team_name not in self.collected_data['teams']:
                try:
                    team_stats = scraper.scrape_team_stats(team_name)
                    if team_stats:
                        self.collected_data['teams'][team_name] = team_stats
                except Exception as e:
                    logger.error(f"Error collecting team stats for {team_name}: {e}")
        
        # Collect H2H data for upcoming matches
        upcoming_matches = [m for m in matches if m.get('status') == 'scheduled']
        for match in upcoming_matches[:10]:  # Limit to first 10 to avoid too many requests
            home_team = match.get('home_team', '')
            away_team = match.get('away_team', '')
            
            if home_team and away_team:
                h2h_key = f"{home_team}_{away_team}"
                if h2h_key not in self.collected_data['h2h_records']:
                    try:
                        h2h_data = scraper.scrape_h2h(home_team, away_team)
                        if h2h_data:
                            self.collected_data['h2h_records'][h2h_key] = h2h_data
                    except Exception as e:
                        logger.error(f"Error collecting H2H for {h2h_key}: {e}")
        
        # Collect odds for upcoming matches
        for match in upcoming_matches[:5]:  # Limit to first 5
            match_id = match.get('id', '')
            if match_id:
                try:
                    odds_data = scraper.scrape_odds(match_id)
                    if odds_data:
                        self.collected_data['odds'][match_id] = odds_data
                except Exception as e:
                    logger.error(f"Error collecting odds for match {match_id}: {e}")
    
    def _merge_data(self) -> Dict:
        """Merge and deduplicate collected data"""
        merged = {
            'matches': [],
            'teams': {},
            'h2h_records': {},
            'odds': {},
            'statistics': {},
            'last_updated': datetime.now().isoformat()
        }
        
        # Merge matches (remove duplicates based on match ID)
        seen_matches = set()
        for match in self.collected_data['matches']:
            match_id = match.get('id', '')
            if match_id and match_id not in seen_matches:
                merged['matches'].append(match)
                seen_matches.add(match_id)
        
        # Merge teams
        merged['teams'] = self.collected_data['teams']
        
        # Merge H2H records
        merged['h2h_records'] = self.collected_data['h2h_records']
        
        # Merge odds
        merged['odds'] = self.collected_data['odds']
        
        # Merge statistics
        merged['statistics'] = self.collected_data['statistics']
        
        return merged
    
    def _save_data(self, data: Dict):
        """Save collected data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save raw data
        raw_file = f"backend/data/raw/data_{timestamp}.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        # Save latest data
        latest_file = "backend/data/processed/latest_data.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Data saved to {raw_file} and {latest_file}")
    
    def get_latest_data(self) -> Dict:
        """Get the latest collected data"""
        try:
            with open("backend/data/processed/latest_data.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("No latest data found, collecting new data")
            return self.collect_all_data()
    
    def get_source_status(self) -> Dict:
        """Get status of all data sources"""
        status = {}
        for source_name, scraper in self.scrapers.items():
            status[source_name] = scraper.get_data_source_status()
        return status
    
    def cleanup(self):
        """Clean up resources"""
        for scraper in self.scrapers.values():
            scraper.cleanup()

# Example usage
if __name__ == "__main__":
    collector = DataCollector()
    
    try:
        # Collect data for the last 7 days and next 7 days
        data = collector.collect_all_data(days_back=7, days_forward=7)
        
        print(f"Collected {len(data['matches'])} matches")
        print(f"Collected data for {len(data['teams'])} teams")
        print(f"Collected {len(data['h2h_records'])} H2H records")
        print(f"Collected odds for {len(data['odds'])} matches")
        
        # Print source status
        status = collector.get_source_status()
        for source, source_status in status.items():
            print(f"{source}: {source_status.status} (Success rate: {source_status.success_rate:.2%})")
    
    finally:
        collector.cleanup()
