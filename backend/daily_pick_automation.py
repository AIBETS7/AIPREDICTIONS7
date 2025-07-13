#!/usr/bin/env python3
"""
Daily pick automation with validation
Ensures only one real pick per day with no fake/imaginary picks
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import create_engine, text
from config.database import DATABASE_URL
from ai_predictor import AIPredictor
from data_collector import DataCollector
import json

def check_existing_pick_today():
    """Check if there's already a pick for today"""
    logger.info("Checking for existing pick today...")
    
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        
        today = datetime.now().date()
        
        # Check if there's already a pick for today
        result = conn.execute(text("""
            SELECT COUNT(*) as count FROM daily_picks 
            WHERE DATE(created_at) = :today
        """), {"today": today})
        
        count = result.fetchone()['count']
        logger.info(f"Found {count} existing picks for today")
        
        conn.close()
        return count > 0
        
    except Exception as e:
        logger.error(f"Error checking existing picks: {e}")
        return False

def validate_real_match(home_team, away_team, match_date):
    """Validate that this is a real match, not fake/imaginary"""
    logger.info(f"Validating match: {home_team} vs {away_team} on {match_date}")
    
    # List of known fake/imaginary team names to filter out
    fake_indicators = [
        'test', 'example', 'demo', 'fake', 'dummy', 'sample',
        'team a', 'team b', 'home team', 'away team',
        'team 1', 'team 2', 'team x', 'team y',
        'home', 'away', 'local', 'visitor'
    ]
    
    # Check for fake team names
    home_lower = home_team.lower()
    away_lower = away_team.lower()
    
    for indicator in fake_indicators:
        if indicator in home_lower or indicator in away_lower:
            logger.warning(f"Potential fake team detected: {home_team} vs {away_team}")
            return False
    
    # Check if teams are too generic
    if len(home_team.strip()) < 3 or len(away_team.strip()) < 3:
        logger.warning(f"Team names too short: {home_team} vs {away_team}")
        return False
    
    # Check if it's the same team
    if home_team.lower().strip() == away_team.lower().strip():
        logger.warning(f"Same team playing against itself: {home_team}")
        return False
    
    logger.info(f"Match validation passed: {home_team} vs {away_team}")
    return True

def generate_daily_pick():
    """Generate one real daily pick with validation"""
    logger.info("Starting daily pick generation...")
    
    # Check if there's already a pick for today
    if check_existing_pick_today():
        logger.info("Pick already exists for today. Skipping generation.")
        return None
    
    try:
        # Initialize AI predictor and data collector
        predictor = AIPredictor()
        data_collector = DataCollector()
        
        # Get latest data
        data = data_collector.get_latest_data()
        
        # Filter upcoming matches
        upcoming_matches = [
            match for match in data.get('matches', [])
            if match.get('status') == 'scheduled'
        ]
        
        if not upcoming_matches:
            logger.error("No upcoming matches found")
            return None
        
        # Filter for real matches only
        real_matches = []
        for match in upcoming_matches:
            if validate_real_match(match.get('home_team'), match.get('away_team'), match.get('time')):
                real_matches.append(match)
        
        if not real_matches:
            logger.error("No real matches found")
            return None
        
        # Take the first real match
        selected_match = real_matches[0]
        
        logger.info(f"Selected real match: {selected_match['home_team']} vs {selected_match['away_team']}")
        
        # Get related data for prediction
        team_data = data.get('teams', {})
        h2h_data = data.get('h2h_records', {})
        odds_data = data.get('odds', {}).get(selected_match.get('id', ''), {})
        
        # Make predictions
        predictions = predictor.make_prediction(selected_match, team_data, h2h_data, odds_data)
        
        if not predictions:
            logger.error("No predictions generated for selected match")
            return None
        
        # Take the highest confidence prediction
        best_prediction = max(predictions, key=lambda x: x.confidence)
        
        # Save to database
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        
        conn.execute(text("""
            INSERT INTO daily_picks (
                home_team, away_team, prediction, prediction_type, 
                confidence, match_date, created_at
            ) VALUES (
                :home_team, :away_team, :prediction, :prediction_type,
                :confidence, :match_date, :created_at
            )
        """), {
            'home_team': selected_match['home_team'],
            'away_team': selected_match['away_team'],
            'prediction': best_prediction.prediction,
            'prediction_type': best_prediction.prediction_type.value,
            'confidence': best_prediction.confidence,
            'match_date': selected_match.get('time'),
            'created_at': datetime.now().isoformat()
        })
        
        conn.close()
        
        logger.info("Daily pick saved successfully")
        
        return {
            'home_team': selected_match['home_team'],
            'away_team': selected_match['away_team'],
            'prediction': best_prediction.prediction,
            'prediction_type': best_prediction.prediction_type.value,
            'confidence': best_prediction.confidence,
            'match_date': selected_match.get('time')
        }
            
    except Exception as e:
        logger.error(f"Error generating daily pick: {e}")
        return None

def main():
    """Main function to run daily pick automation"""
    logger.info("Starting daily pick automation...")
    
    # Generate pick
    pick = generate_daily_pick()
    
    if pick:
        logger.info(f"Daily pick generated successfully: {pick['home_team']} vs {pick['away_team']} - {pick['prediction']}")
    else:
        logger.info("No daily pick generated (already exists or no valid predictions)")

if __name__ == "__main__":
    main() 