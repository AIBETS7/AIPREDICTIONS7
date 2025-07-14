#!/usr/bin/env python3
"""
Clean daily picks - Remove fake/imaginary picks and ensure only one real pick per day
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from loguru import logger
import json
import requests

def check_live_picks():
    """Check picks from the live API"""
    logger.info("Checking live picks from API...")
    
    try:
        # Get picks from the live API
        response = requests.get('https://my-football-predictions.onrender.com/api/daily-picks')
        if response.status_code == 200:
            picks = response.json()
            logger.info(f"Found {len(picks)} picks in live system")
            
            # Group by date
            picks_by_date = {}
            for pick in picks:
                if 'created_at' in pick and pick['created_at']:
                    try:
                        # Parse the date string
                        dt = datetime.fromisoformat(pick['created_at'].replace('Z', '+00:00'))
                        date_key = dt.date()
                        
                        if date_key not in picks_by_date:
                            picks_by_date[date_key] = []
                        picks_by_date[date_key].append(pick)
                    except Exception as e:
                        logger.error(f"Could not parse date for pick {pick.get('id')}: {e}")
                        continue
            
            # Analyze picks by date
            logger.info(f"Picks grouped by {len(picks_by_date)} dates:")
            for date, date_picks in picks_by_date.items():
                logger.info(f"\nDate: {date}")
                logger.info(f"Number of picks: {len(date_picks)}")
                
                for i, pick in enumerate(date_picks, 1):
                    logger.info(f"  {i}. {pick.get('home_team', 'N/A')} vs {pick.get('away_team', 'N/A')}")
                    logger.info(f"     Prediction: {pick.get('prediction', 'N/A')}")
                    logger.info(f"     Type: {pick.get('prediction_type', 'N/A')}")
                    logger.info(f"     ID: {pick.get('id', 'N/A')}")
                    
                    # Check if this looks like a real match
                    home_team = pick.get('home_team', '').strip()
                    away_team = pick.get('away_team', '').strip()
                    
                    # Identify potential fake picks
                    fake_indicators = [
                        'test', 'example', 'fake', 'dummy', 'sample',
                        'team a', 'team b', 'home', 'away',
                        'equipo a', 'equipo b', 'casa', 'visitante'
                    ]
                    
                    is_fake = any(indicator in home_team.lower() or indicator in away_team.lower() 
                                for indicator in fake_indicators)
                    
                    if is_fake:
                        logger.warning(f"    ⚠️  POTENTIAL FAKE PICK DETECTED!")
                    else:
                        logger.success(f"    ✅ Looks like a real match")
            
            return picks_by_date
        else:
            logger.error(f"Failed to get picks from API: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error checking live picks: {e}")
        return None

def identify_fake_picks(picks_by_date):
    """Identify which picks are fake/imaginary"""
    fake_picks = []
    real_picks = []
    
    for date, date_picks in picks_by_date.items():
        for pick in date_picks:
            home_team = pick.get('home_team', '').strip()
            away_team = pick.get('away_team', '').strip()
            
            # Check for fake indicators
            fake_indicators = [
                'test', 'example', 'fake', 'dummy', 'sample',
                'team a', 'team b', 'home', 'away',
                'equipo a', 'equipo b', 'casa', 'visitante'
            ]
            
            is_fake = any(indicator in home_team.lower() or indicator in away_team.lower() 
                        for indicator in fake_indicators)
            
            if is_fake:
                fake_picks.append(pick)
            else:
                real_picks.append(pick)
    
    return fake_picks, real_picks

def main():
    """Main function to clean daily picks"""
    logger.info("Starting daily picks cleanup...")
    
    # Check current picks
    picks_by_date = check_live_picks()
    
    if not picks_by_date:
        logger.error("Could not retrieve picks from API")
        return
    
    # Identify fake and real picks
    fake_picks, real_picks = identify_fake_picks(picks_by_date)
    
    logger.info(f"\n📊 ANALYSIS RESULTS:")
    logger.info(f"Total picks found: {sum(len(picks) for picks in picks_by_date.values())}")
    logger.info(f"Fake/imaginary picks: {len(fake_picks)}")
    logger.info(f"Real picks: {len(real_picks)}")
    
    if fake_picks:
        logger.warning(f"\n🚨 FAKE PICKS TO REMOVE:")
        for pick in fake_picks:
            logger.warning(f"  - {pick.get('home_team')} vs {pick.get('away_team')} (ID: {pick.get('id')})")
    
    # Group real picks by date
    real_picks_by_date = {}
    for pick in real_picks:
        dt = datetime.fromisoformat(pick['created_at'].replace('Z', '+00:00'))
        date_key = dt.date()
        if date_key not in real_picks_by_date:
            real_picks_by_date[date_key] = []
        real_picks_by_date[date_key].append(pick)
    
    logger.info(f"\n📅 REAL PICKS BY DATE:")
    for date, picks in real_picks_by_date.items():
        logger.info(f"  {date}: {len(picks)} pick(s)")
        if len(picks) > 1:
            logger.warning(f"    ⚠️  Multiple picks on {date} - should keep only the best one")
    
    logger.info(f"\n✅ RECOMMENDATIONS:")
    logger.info(f"1. Remove {len(fake_picks)} fake/imaginary picks")
    logger.info(f"2. Keep only 1 real pick per day")
    logger.info(f"3. Total picks after cleanup: {len(real_picks_by_date)} (one per day)")

if __name__ == "__main__":
    main() 