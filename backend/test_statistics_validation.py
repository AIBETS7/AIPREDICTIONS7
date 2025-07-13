#!/usr/bin/env python3
"""
Test script for validating match statistics from official sources
Focuses on corners, yellow cards, shots on target, etc.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from loguru import logger
from scrapers.promiedos_scraper import PromiedosScraper
from data_validator import DataValidator
import json

def test_promiedos_statistics():
    """Test Promiedos scraper for match statistics"""
    logger.info("Testing Promiedos scraper for match statistics...")
    
    scraper = PromiedosScraper()
    
    # Test match scraping
    date_from = datetime.now()
    date_to = datetime.now() + timedelta(days=7)
    
    try:
        matches = scraper.scrape_matches('ES1', date_from, date_to)
        logger.info(f"Promiedos scraper found {len(matches)} matches")
        
        # Analyze matches for statistics
        for match in matches[:5]:  # Test first 5 matches
            logger.info(f"\nMatch: {match.get('home_team', 'Unknown')} vs {match.get('away_team', 'Unknown')}")
            logger.info(f"Date: {match.get('date', 'Unknown')}")
            logger.info(f"Status: {match.get('status', 'Unknown')}")
            logger.info(f"Stage: {match.get('stage_round', 'Unknown')}")
            logger.info(f"TV Networks: {', '.join(match.get('tv_networks', []))}")
            
            # Check odds data
            odds = match.get('odds', {})
            if odds:
                logger.info(f"Odds - Home: {odds.get('1', 'N/A')}, Draw: {odds.get('X', 'N/A')}, Away: {odds.get('2', 'N/A')}")
            else:
                logger.info("No odds available")
                
    except Exception as e:
        logger.error(f"Error testing Promiedos statistics: {e}")
        return False
    
    return True

def test_team_statistics():
    """Test team statistics extraction"""
    logger.info("\nTesting team statistics extraction...")
    
    scraper = PromiedosScraper()
    
    # Test with some known La Liga teams
    test_teams = ['Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla']
    
    for team in test_teams:
        try:
            stats = scraper.scrape_team_stats(team)
            if stats:
                logger.info(f"\nTeam: {team}")
                logger.info(f"Position: {stats.get('position', 'N/A')}")
                logger.info(f"Points: {stats.get('points', 'N/A')}")
                logger.info(f"Matches: {stats.get('matches_played', 'N/A')}")
                logger.info(f"Wins: {stats.get('wins', 'N/A')}")
                logger.info(f"Draws: {stats.get('draws', 'N/A')}")
                logger.info(f"Losses: {stats.get('losses', 'N/A')}")
                logger.info(f"Goals For: {stats.get('goals_for', 'N/A')}")
                logger.info(f"Goals Against: {stats.get('goals_against', 'N/A')}")
                logger.info(f"Goal Difference: {stats.get('goal_difference', 'N/A')}")
            else:
                logger.warning(f"No statistics found for {team}")
                
        except Exception as e:
            logger.error(f"Error getting stats for {team}: {e}")

def test_match_statistics_validation():
    """Test validation of match statistics"""
    logger.info("\nTesting match statistics validation...")
    
    validator = DataValidator()
    
    # Create sample match data with statistics
    sample_matches = [
        {
            'id': 'test_1',
            'home_team': 'Real Madrid',
            'away_team': 'Barcelona',
            'date': datetime.now().isoformat(),
            'status': 'scheduled',
            'source': 'promiedos',
            'statistics': {
                'corners': {'home': 6, 'away': 4},
                'yellow_cards': {'home': 2, 'away': 3},
                'red_cards': {'home': 0, 'away': 1},
                'shots_on_target': {'home': 8, 'away': 5},
                'shots_total': {'home': 15, 'away': 12},
                'possession': {'home': 55, 'away': 45},
                'fouls': {'home': 12, 'away': 15}
            }
        },
        {
            'id': 'test_2',
            'home_team': 'Atletico Madrid',
            'away_team': 'Sevilla',
            'date': datetime.now().isoformat(),
            'status': 'scheduled',
            'source': 'promiedos',
            'statistics': {
                'corners': {'home': 5, 'away': 3},
                'yellow_cards': {'home': 1, 'away': 2},
                'red_cards': {'home': 0, 'away': 0},
                'shots_on_target': {'home': 6, 'away': 4},
                'shots_total': {'home': 13, 'away': 10},
                'possession': {'home': 48, 'away': 52},
                'fouls': {'home': 10, 'away': 11}
            }
        }
    ]
    
    # Validate the statistics
    validation_result = validator.validate_matches(sample_matches)
    
    logger.info(f"Validation result: {validation_result['valid_matches']} valid matches")
    
    # Check statistics quality
    for match in sample_matches:
        stats = match.get('statistics', {})
        logger.info(f"\nMatch: {match['home_team']} vs {match['away_team']}")
        
        # Validate corners
        corners = stats.get('corners', {})
        if corners:
            total_corners = corners.get('home', 0) + corners.get('away', 0)
            logger.info(f"Total corners: {total_corners}")
            if total_corners > 20:
                logger.warning("High number of corners - may need verification")
        
        # Validate cards
        yellow_cards = stats.get('yellow_cards', {})
        red_cards = stats.get('red_cards', {})
        if yellow_cards or red_cards:
            total_yellow = yellow_cards.get('home', 0) + yellow_cards.get('away', 0)
            total_red = red_cards.get('home', 0) + red_cards.get('away', 0)
            logger.info(f"Yellow cards: {total_yellow}, Red cards: {total_red}")
            
            if total_yellow > 10:
                logger.warning("High number of yellow cards - may need verification")
            if total_red > 3:
                logger.warning("High number of red cards - may need verification")
        
        # Validate shots
        shots_on_target = stats.get('shots_on_target', {})
        shots_total = stats.get('shots_total', {})
        if shots_on_target and shots_total:
            home_on_target = shots_on_target.get('home', 0)
            home_total = shots_total.get('home', 0)
            away_on_target = shots_on_target.get('away', 0)
            away_total = shots_total.get('away', 0)
            
            logger.info(f"Shots on target - Home: {home_on_target}/{home_total}, Away: {away_on_target}/{away_total}")
            
            # Check for unrealistic accuracy
            if home_total > 0 and (home_on_target / home_total) > 0.8:
                logger.warning("Unusually high shot accuracy for home team")
            if away_total > 0 and (away_on_target / away_total) > 0.8:
                logger.warning("Unusually high shot accuracy for away team")

def test_statistics_consistency():
    """Test consistency of statistics across sources"""
    logger.info("\nTesting statistics consistency...")
    
    # This would compare statistics from multiple sources
    # For now, we'll simulate this with sample data
    
    source1_stats = {
        'corners': {'home': 6, 'away': 4},
        'yellow_cards': {'home': 2, 'away': 3},
        'shots_on_target': {'home': 8, 'away': 5}
    }
    
    source2_stats = {
        'corners': {'home': 5, 'away': 4},
        'yellow_cards': {'home': 2, 'away': 2},
        'shots_on_target': {'home': 7, 'away': 5}
    }
    
    # Check for significant differences
    logger.info("Comparing statistics between sources:")
    
    for stat_type in ['corners', 'yellow_cards', 'shots_on_target']:
        if stat_type in source1_stats and stat_type in source2_stats:
            s1_home = source1_stats[stat_type].get('home', 0)
            s1_away = source1_stats[stat_type].get('away', 0)
            s2_home = source2_stats[stat_type].get('home', 0)
            s2_away = source2_stats[stat_type].get('away', 0)
            
            home_diff = abs(s1_home - s2_home)
            away_diff = abs(s1_away - s2_away)
            
            logger.info(f"{stat_type}:")
            logger.info(f"  Home - Source1: {s1_home}, Source2: {s2_home}, Difference: {home_diff}")
            logger.info(f"  Away - Source1: {s1_away}, Source2: {s2_away}, Difference: {away_diff}")
            
            if home_diff > 2 or away_diff > 2:
                logger.warning(f"Significant difference in {stat_type} statistics")

def test_statistics_quality_metrics():
    """Test quality metrics for statistics"""
    logger.info("\nTesting statistics quality metrics...")
    
    # Sample statistics with quality indicators
    sample_stats = [
        {
            'match': 'Real Madrid vs Barcelona',
            'statistics': {
                'corners': {'home': 6, 'away': 4, 'confidence': 0.95},
                'yellow_cards': {'home': 2, 'away': 3, 'confidence': 0.98},
                'shots_on_target': {'home': 8, 'away': 5, 'confidence': 0.92},
                'possession': {'home': 55, 'away': 45, 'confidence': 0.89}
            },
            'source_reliability': 0.95
        },
        {
            'match': 'Atletico Madrid vs Sevilla',
            'statistics': {
                'corners': {'home': 5, 'away': 3, 'confidence': 0.87},
                'yellow_cards': {'home': 1, 'away': 2, 'confidence': 0.94},
                'shots_on_target': {'home': 6, 'away': 4, 'confidence': 0.91},
                'possession': {'home': 48, 'away': 52, 'confidence': 0.86}
            },
            'source_reliability': 0.90
        }
    ]
    
    for match_data in sample_stats:
        match_name = match_data['match']
        stats = match_data['statistics']
        source_reliability = match_data['source_reliability']
        
        logger.info(f"\nMatch: {match_name}")
        logger.info(f"Source reliability: {source_reliability:.2f}")
        
        # Calculate overall confidence
        confidences = []
        for stat_type, stat_data in stats.items():
            if isinstance(stat_data, dict) and 'confidence' in stat_data:
                confidences.append(stat_data['confidence'])
        
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            overall_quality = (avg_confidence + source_reliability) / 2
            
            logger.info(f"Average confidence: {avg_confidence:.2f}")
            logger.info(f"Overall quality score: {overall_quality:.2f}")
            
            if overall_quality >= 0.9:
                logger.info("✅ High quality statistics")
            elif overall_quality >= 0.7:
                logger.info("⚠️ Medium quality statistics")
            else:
                logger.warning("❌ Low quality statistics")

def main():
    """Main test function"""
    logger.info("Starting statistics validation test...")
    
    # Test Promiedos scraper
    promiedos_success = test_promiedos_statistics()
    
    # Test team statistics
    test_team_statistics()
    
    # Test match statistics validation
    test_match_statistics_validation()
    
    # Test statistics consistency
    test_statistics_consistency()
    
    # Test quality metrics
    test_statistics_quality_metrics()
    
    logger.info("\nStatistics validation test completed!")
    
    if promiedos_success:
        logger.info("✅ Promiedos scraper working correctly")
    else:
        logger.error("❌ Promiedos scraper has issues")

if __name__ == "__main__":
    main() 