#!/usr/bin/env python3
"""
Test script for official source scrapers
Tests La Liga official and Promiedos scrapers to ensure they provide reliable data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from loguru import logger
from scrapers.laliga_scraper import LaLigaScraper
from scrapers.promiedos_scraper import PromiedosScraper
from data_validator import DataValidator

def test_laliga_scraper():
    """Test La Liga official scraper"""
    logger.info("Testing La Liga official scraper...")
    
    scraper = LaLigaScraper()
    
    # Test match scraping
    date_from = datetime.now()
    date_to = datetime.now() + timedelta(days=7)
    
    try:
        matches = scraper.scrape_matches('ES1', date_from, date_to)
        logger.info(f"La Liga scraper found {len(matches)} matches")
        
        if matches:
            logger.info("Sample match data:")
            for match in matches[:3]:  # Show first 3 matches
                logger.info(f"  {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')}")
                logger.info(f"    Date: {match.get('date', 'N/A')}")
                logger.info(f"    Status: {match.get('status', 'N/A')}")
                logger.info(f"    Source: {match.get('source', 'N/A')}")
                logger.info("")
        
        return matches
        
    except Exception as e:
        logger.error(f"Error testing La Liga scraper: {e}")
        return []

def test_promiedos_scraper():
    """Test Promiedos scraper"""
    logger.info("Testing Promiedos scraper...")
    
    scraper = PromiedosScraper()
    
    # Test match scraping
    date_from = datetime.now()
    date_to = datetime.now() + timedelta(days=7)
    
    try:
        matches = scraper.scrape_matches('ES1', date_from, date_to)
        logger.info(f"Promiedos scraper found {len(matches)} matches")
        
        if matches:
            logger.info("Sample match data:")
            for match in matches[:3]:  # Show first 3 matches
                logger.info(f"  {match.get('home_team', 'N/A')} vs {match.get('away_team', 'N/A')}")
                logger.info(f"    Date: {match.get('date', 'N/A')}")
                logger.info(f"    Status: {match.get('status', 'N/A')}")
                logger.info(f"    Source: {match.get('source', 'N/A')}")
                logger.info("")
        
        return matches
        
    except Exception as e:
        logger.error(f"Error testing Promiedos scraper: {e}")
        return []

def test_data_validation():
    """Test data validation with sample data"""
    logger.info("Testing data validation...")
    
    validator = DataValidator()
    
    # Create sample data from multiple sources
    sample_data = {
        'matches': [
            {
                'id': 'test_1',
                'home_team': 'Real Madrid',
                'away_team': 'Barcelona',
                'date': '2025-01-20T20:00:00',
                'status': 'scheduled',
                'source': 'laliga_official'
            },
            {
                'id': 'test_2',
                'home_team': 'Real Madrid',
                'away_team': 'Barcelona',
                'date': '2025-01-20T20:00:00',
                'status': 'scheduled',
                'source': 'promiedos'
            },
            {
                'id': 'test_3',
                'home_team': 'Atletico Madrid',
                'away_team': 'Sevilla',
                'date': '2025-01-21T18:00:00',
                'status': 'scheduled',
                'source': 'laliga_official'
            }
        ]
    }
    
    try:
        validation_result = validator.validate_matches(sample_data)
        
        logger.info("Validation result:")
        logger.info(f"  Valid matches: {len(validation_result['valid_matches'])}")
        logger.info(f"  Validation errors: {len(validation_result['validation_errors'])}")
        logger.info(f"  Validation rate: {validation_result['validation_summary']['validation_rate']:.2%}")
        
        if validation_result['valid_matches']:
            logger.info("Validated matches:")
            for match in validation_result['valid_matches']:
                logger.info(f"  {match['home_team']} vs {match['away_team']}")
                logger.info(f"    Confidence: {match.get('validation_metadata', {}).get('confidence_score', 0):.2f}")
                logger.info(f"    Sources: {match.get('validation_metadata', {}).get('sources_confirmed', [])}")
                logger.info("")
        
        return validation_result
        
    except Exception as e:
        logger.error(f"Error testing data validation: {e}")
        return None

def test_integration():
    """Test integration of all components"""
    logger.info("Testing full integration...")
    
    # Collect data from both sources
    laliga_matches = test_laliga_scraper()
    promiedos_matches = test_promiedos_scraper()
    
    # Combine data
    combined_data = {
        'matches': laliga_matches + promiedos_matches
    }
    
    # Validate combined data
    validator = DataValidator()
    validation_result = validator.validate_matches(combined_data)
    
    # Filter for predictions
    suitable_matches = validator.filter_matches_for_predictions(validation_result['valid_matches'])
    
    logger.info("Integration test results:")
    logger.info(f"  Total matches collected: {len(combined_data['matches'])}")
    logger.info(f"  Valid matches: {len(validation_result['valid_matches'])}")
    logger.info(f"  Suitable for predictions: {len(suitable_matches)}")
    
    if suitable_matches:
        logger.info("Matches suitable for predictions:")
        for match in suitable_matches:
            logger.info(f"  {match['home_team']} vs {match['away_team']} - {match['date']}")
            logger.info(f"    Confidence: {match.get('validation_metadata', {}).get('confidence_score', 0):.2f}")
    
    return {
        'laliga_matches': len(laliga_matches),
        'promiedos_matches': len(promiedos_matches),
        'valid_matches': len(validation_result['valid_matches']),
        'suitable_matches': len(suitable_matches)
    }

def main():
    """Main test function"""
    logger.info("Starting official sources test...")
    
    # Test individual scrapers
    test_laliga_scraper()
    test_promiedos_scraper()
    
    # Test data validation
    test_data_validation()
    
    # Test full integration
    integration_results = test_integration()
    
    logger.info("Test completed!")
    logger.info(f"Integration results: {integration_results}")

if __name__ == "__main__":
    main() 