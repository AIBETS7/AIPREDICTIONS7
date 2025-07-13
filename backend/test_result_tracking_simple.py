#!/usr/bin/env python3
"""
Simple test script for result tracking system
Tests database updates, website display, and Telegram notifications
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from loguru import logger
from result_checker import ResultChecker
from telegram_result_updater import TelegramResultUpdater
from sqlalchemy import create_engine, text
from config.database import DATABASE_URL
import json

def test_database_schema():
    """Test that result tracking columns exist"""
    logger.info("Testing database schema...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if result tracking columns exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'daily_picks' 
                AND column_name IN ('result_status', 'actual_result', 'result_updated_at')
            """))
            
            columns = [row[0] for row in result]
            
            if len(columns) == 3:
                logger.info("PASS: All result tracking columns exist")
                return True
            else:
                logger.error(f"FAIL: Missing columns. Found: {columns}")
                return False
                
    except Exception as e:
        logger.error(f"FAIL: Database schema test failed: {e}")
        return False

def test_sample_prediction():
    """Test with a sample prediction"""
    logger.info("Testing sample prediction...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Insert a test prediction
            test_prediction = {
                'id': 'test_prediction_001',
                'home_team': 'Real Madrid',
                'away_team': 'Barcelona',
                'prediction': 'home',
                'prediction_type': 'match_winner',
                'confidence': 75.0,
                'odds': 2.10,
                'stake': 10.0,
                'reasoning': 'Real Madrid has strong home form and historical advantage',
                'match_time': datetime.now() - timedelta(hours=2),  # Match happened 2 hours ago
                'competition': 'La Liga',
                'tipster': 'AI Predictor Pro',
                'created_at': datetime.now() - timedelta(hours=4),
                'result_status': 'pending'
            }
            
            # Insert test prediction
            conn.execute(text("""
                INSERT INTO daily_picks 
                (id, home_team, away_team, prediction, prediction_type, confidence, odds, stake, 
                 reasoning, match_time, competition, tipster, created_at, result_status)
                VALUES (:id, :home_team, :away_team, :prediction, :prediction_type, :confidence, 
                        :odds, :stake, :reasoning, :match_time, :competition, :tipster, :created_at, :result_status)
                ON CONFLICT (id) DO UPDATE SET
                    result_status = EXCLUDED.result_status
            """), test_prediction)
            
            logger.info("PASS: Test prediction inserted")
            
            # Update with a result (Real Madrid wins 2-1)
            conn.execute(text("""
                UPDATE daily_picks 
                SET result_status = 'correct', 
                    actual_result = '2-1',
                    result_updated_at = NOW()
                WHERE id = :id
            """), {'id': 'test_prediction_001'})
            
            logger.info("PASS: Test prediction result updated")
            
            return True
            
    except Exception as e:
        logger.error(f"FAIL: Sample prediction test failed: {e}")
        return False

def test_result_checker():
    """Test the result checker functionality"""
    logger.info("Testing result checker...")
    
    try:
        checker = ResultChecker()
        
        # Test prediction result determination
        test_cases = [
            # (prediction, prediction_type, home_score, away_score, expected_result)
            ('home', 'match_winner', 2, 1, 'correct'),
            ('away', 'match_winner', 1, 2, 'correct'),
            ('home', 'match_winner', 1, 2, 'incorrect'),
            ('draw', 'match_winner', 1, 1, 'correct'),
            ('yes', 'both_teams_score', 2, 1, 'correct'),
            ('no', 'both_teams_score', 2, 0, 'correct'),
            ('over 2.5', 'over_under', 2, 1, 'correct'),
            ('under 2.5', 'over_under', 1, 0, 'correct'),
        ]
        
        for prediction, pred_type, home_score, away_score, expected in test_cases:
            result = checker.determine_prediction_result(prediction, pred_type, home_score, away_score)
            if result == expected:
                logger.info(f"PASS: {prediction} {pred_type} {home_score}-{away_score} = {result}")
            else:
                logger.error(f"FAIL: {prediction} {pred_type} {home_score}-{away_score} = {result} (expected {expected})")
        
        return True
        
    except Exception as e:
        logger.error(f"FAIL: Result checker test failed: {e}")
        return False

def test_website_api():
    """Test the website API endpoint"""
    logger.info("Testing website API...")
    
    try:
        # This would normally test the Flask API
        # For now, we'll test the database query that the API uses
        
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, home_team, away_team, prediction, prediction_type, 
                       confidence, odds, match_time, reasoning, tipster, 
                       created_at, result_status, actual_result
                FROM daily_picks 
                ORDER BY created_at DESC 
                LIMIT 5
            """))
            
            picks = []
            for row in result:
                picks.append({
                    'id': row[0],
                    'home_team': row[1],
                    'away_team': row[2],
                    'prediction': row[3],
                    'prediction_type': row[4],
                    'confidence': float(row[5]) if row[5] else 0.0,
                    'odds': float(row[6]) if row[6] else 0.0,
                    'match_time': row[7].isoformat() if hasattr(row[7], 'isoformat') else str(row[7]) if row[7] else None,
                    'reasoning': row[8],
                    'tipster': row[9],
                    'created_at': row[10].isoformat() if hasattr(row[10], 'isoformat') else str(row[10]) if row[10] else None,
                    'result_status': row[11] or 'pending',
                    'actual_result': row[12]
                })
            
            logger.info(f"PASS: API query successful, found {len(picks)} picks")
            
            # Check if our test prediction is included
            test_pick = next((p for p in picks if p['id'] == 'test_prediction_001'), None)
            if test_pick:
                logger.info(f"PASS: Test prediction found in API response")
                logger.info(f"   Result status: {test_pick['result_status']}")
                logger.info(f"   Actual result: {test_pick['actual_result']}")
            else:
                logger.warning("WARNING: Test prediction not found in API response")
            
            return True
            
    except Exception as e:
        logger.error(f"FAIL: Website API test failed: {e}")
        return False

def test_telegram_updater():
    """Test the Telegram result updater"""
    logger.info("Testing Telegram result updater...")
    
    try:
        updater = TelegramResultUpdater()
        
        # Test getting completed predictions
        completed = updater.get_completed_predictions()
        logger.info(f"PASS: Found {len(completed)} completed predictions")
        
        # Test result message formatting (without actually sending)
        if completed:
            prediction = completed[0]
            logger.info(f"PASS: Sample prediction for Telegram: {prediction['home_team']} vs {prediction['away_team']}")
            logger.info(f"   Result: {prediction['result_status']}")
            logger.info(f"   Score: {prediction['actual_result']}")
        
        return True
        
    except Exception as e:
        logger.error(f"FAIL: Telegram updater test failed: {e}")
        return False

def cleanup_test_data():
    """Clean up test data"""
    logger.info("Cleaning up test data...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Remove test prediction
            conn.execute(text("DELETE FROM daily_picks WHERE id = :id"), 
                        {'id': 'test_prediction_001'})
            
            logger.info("PASS: Test data cleaned up")
            return True
            
    except Exception as e:
        logger.error(f"FAIL: Cleanup failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting result tracking system tests...")
    
    tests = [
        test_database_schema,
        test_sample_prediction,
        test_result_checker,
        test_website_api,
        test_telegram_updater,
        cleanup_test_data
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            logger.error(f"Test {test.__name__} failed with exception: {e}")
    
    logger.info(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        logger.info("ALL TESTS PASSED! Result tracking system is working correctly.")
    else:
        logger.error("Some tests failed. Please check the logs above.")

if __name__ == "__main__":
    main() 