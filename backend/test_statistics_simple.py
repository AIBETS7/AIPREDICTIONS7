#!/usr/bin/env python3
"""
Simplified test script for validating match statistics
Focuses on corners, yellow cards, shots on target, etc.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from loguru import logger
import json

def test_statistics_validation():
    """Test validation of match statistics"""
    logger.info("Testing match statistics validation...")
    
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
                logger.warning("⚠️ High number of corners - may need verification")
            elif total_corners < 3:
                logger.warning("⚠️ Low number of corners - may need verification")
            else:
                logger.info("✅ Corner count looks reasonable")
        
        # Validate cards
        yellow_cards = stats.get('yellow_cards', {})
        red_cards = stats.get('red_cards', {})
        if yellow_cards or red_cards:
            total_yellow = yellow_cards.get('home', 0) + yellow_cards.get('away', 0)
            total_red = red_cards.get('home', 0) + red_cards.get('away', 0)
            logger.info(f"Yellow cards: {total_yellow}, Red cards: {total_red}")
            
            if total_yellow > 10:
                logger.warning("⚠️ High number of yellow cards - may need verification")
            elif total_yellow < 1:
                logger.warning("⚠️ Low number of yellow cards - may need verification")
            else:
                logger.info("✅ Yellow card count looks reasonable")
                
            if total_red > 3:
                logger.warning("⚠️ High number of red cards - may need verification")
            else:
                logger.info("✅ Red card count looks reasonable")
        
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
            if home_total > 0:
                home_accuracy = (home_on_target / home_total) * 100
                logger.info(f"Home team accuracy: {home_accuracy:.1f}%")
                if home_accuracy > 80:
                    logger.warning("⚠️ Unusually high shot accuracy for home team")
                elif home_accuracy < 20:
                    logger.warning("⚠️ Unusually low shot accuracy for home team")
                else:
                    logger.info("✅ Home team accuracy looks reasonable")
                    
            if away_total > 0:
                away_accuracy = (away_on_target / away_total) * 100
                logger.info(f"Away team accuracy: {away_accuracy:.1f}%")
                if away_accuracy > 80:
                    logger.warning("⚠️ Unusually high shot accuracy for away team")
                elif away_accuracy < 20:
                    logger.warning("⚠️ Unusually low shot accuracy for away team")
                else:
                    logger.info("✅ Away team accuracy looks reasonable")
        
        # Validate possession
        possession = stats.get('possession', {})
        if possession:
            home_possession = possession.get('home', 0)
            away_possession = possession.get('away', 0)
            total_possession = home_possession + away_possession
            
            logger.info(f"Possession - Home: {home_possession}%, Away: {away_possession}%")
            
            if abs(total_possession - 100) > 5:
                logger.warning("⚠️ Possession percentages don't add up to ~100%")
            else:
                logger.info("✅ Possession percentages look correct")

def test_statistics_consistency():
    """Test consistency of statistics across sources"""
    logger.info("\nTesting statistics consistency...")
    
    # Simulate data from multiple sources
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
            
            logger.info(f"\n{stat_type}:")
            logger.info(f"  Home - Source1: {s1_home}, Source2: {s2_home}, Difference: {home_diff}")
            logger.info(f"  Away - Source1: {s1_away}, Source2: {s2_away}, Difference: {away_diff}")
            
            if home_diff > 2 or away_diff > 2:
                logger.warning(f"⚠️ Significant difference in {stat_type} statistics")
            else:
                logger.info(f"✅ {stat_type} statistics are consistent")

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

def test_statistics_ranges():
    """Test realistic ranges for different statistics"""
    logger.info("\nTesting realistic statistics ranges...")
    
    # Define realistic ranges for different statistics
    realistic_ranges = {
        'corners': {'min': 3, 'max': 20, 'typical': '8-12'},
        'yellow_cards': {'min': 1, 'max': 10, 'typical': '3-6'},
        'red_cards': {'min': 0, 'max': 3, 'typical': '0-1'},
        'shots_on_target': {'min': 2, 'max': 15, 'typical': '5-10'},
        'shots_total': {'min': 5, 'max': 25, 'typical': '10-18'},
        'possession': {'min': 30, 'max': 70, 'typical': '40-60'},
        'fouls': {'min': 8, 'max': 25, 'typical': '12-18'}
    }
    
    # Test sample data against these ranges
    test_data = {
        'corners': 15,
        'yellow_cards': 4,
        'red_cards': 1,
        'shots_on_target': 8,
        'shots_total': 16,
        'possession': 52,
        'fouls': 14
    }
    
    for stat_type, value in test_data.items():
        if stat_type in realistic_ranges:
            range_info = realistic_ranges[stat_type]
            min_val = range_info['min']
            max_val = range_info['max']
            typical = range_info['typical']
            
            logger.info(f"\n{stat_type}: {value}")
            logger.info(f"Realistic range: {min_val}-{max_val}, Typical: {typical}")
            
            if min_val <= value <= max_val:
                logger.info("✅ Value is within realistic range")
            else:
                logger.warning("⚠️ Value is outside realistic range")

def main():
    """Main test function"""
    logger.info("Starting simplified statistics validation test...")
    
    # Test basic statistics validation
    test_statistics_validation()
    
    # Test statistics consistency
    test_statistics_consistency()
    
    # Test quality metrics
    test_statistics_quality_metrics()
    
    # Test realistic ranges
    test_statistics_ranges()
    
    logger.info("\n✅ Simplified statistics validation test completed!")

if __name__ == "__main__":
    main() 