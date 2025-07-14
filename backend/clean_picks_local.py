#!/usr/bin/env python3
"""
Clean daily picks locally - Remove fake/imaginary picks and ensure only one real pick per day
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from loguru import logger
import sqlite3
from dateutil.parser import parse as parse_date

def get_db_connection():
    """Get connection to local SQLite database"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'football_predictions.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def check_current_picks():
    """Check all current daily picks from local database"""
    logger.info("Checking current daily picks from local database...")
    
    try:
        conn = get_db_connection()
        if not conn:
            return None
        
        cursor = conn.cursor()
        
        # Get all picks ordered by creation date
        query = """
        SELECT id, match_id, home_team, away_team, prediction, prediction_type, 
               confidence, odds, match_time, reasoning, tipster, 
               created_at, expires_at
        FROM daily_picks 
        ORDER BY created_at DESC
        """
        
        cursor.execute(query)
        picks = []
        
        for row in cursor.fetchall():
            pick = dict(row)
            picks.append(pick)
        
        cursor.close()
        conn.close()
        
        logger.info(f"Found {len(picks)} picks in local database")
        return picks
        
    except Exception as e:
        logger.error(f"Error checking picks: {e}")
        return None

def identify_fake_picks(picks):
    """Identify which picks are fake/imaginary"""
    fake_picks = []
    real_picks = []
    
    for pick in picks:
        home_team = pick.get('home_team', '').strip()
        away_team = pick.get('away_team', '').strip()
        
        # Check for fake indicators
        fake_indicators = [
            'test', 'example', 'fake', 'dummy', 'sample',
            'team a', 'team b', 'home', 'away',
            'equipo a', 'equipo b', 'casa', 'visitante',
            'team1', 'team2', 'equipo1', 'equipo2'
        ]
        
        # Check for non-football sports
        non_football_indicators = [
            'wimbledon', 'tennis', 'alcaraz', 'djokovic',
            'summer_friendly', 'friendly'
        ]
        
        is_fake = any(indicator in home_team.lower() or indicator in away_team.lower() 
                    for indicator in fake_indicators)
        
        # Check for non-football sports
        is_non_football = any(indicator in home_team.lower() or indicator in away_team.lower() or 
                             indicator in pick.get('match_id', '').lower()
                             for indicator in non_football_indicators)
        
        # Consider both fake and non-football picks as invalid
        is_invalid = is_fake or is_non_football
        
        if is_invalid:
            fake_picks.append(pick)
        else:
            real_picks.append(pick)
    
    return fake_picks, real_picks

def group_picks_by_date(picks):
    """Group picks by date"""
    picks_by_date = {}
    
    for pick in picks:
        if pick.get('created_at'):
            try:
                if isinstance(pick['created_at'], str):
                    dt = parse_date(pick['created_at'])
                else:
                    dt = pick['created_at']
                date_key = dt.date()
                
                if date_key not in picks_by_date:
                    picks_by_date[date_key] = []
                picks_by_date[date_key].append(pick)
            except Exception as e:
                logger.error(f"Could not parse date for pick {pick.get('id')}: {e}")
                continue
    
    return picks_by_date

def delete_fake_picks(fake_picks):
    """Delete fake picks from database"""
    if not fake_picks:
        logger.info("No fake picks to delete")
        return
    
    try:
        conn = get_db_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        for pick in fake_picks:
            pick_id = pick.get('id')
            home_team = pick.get('home_team', 'N/A')
            away_team = pick.get('away_team', 'N/A')
            
            logger.warning(f"Deleting fake pick: {home_team} vs {away_team} (ID: {pick_id})")
            
            cursor.execute("DELETE FROM daily_picks WHERE id = ?", (pick_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.success(f"Deleted {len(fake_picks)} fake picks")
        
    except Exception as e:
        logger.error(f"Error deleting fake picks: {e}")

def keep_best_pick_per_day(real_picks_by_date):
    """Keep only the best pick per day"""
    picks_to_delete = []
    
    for date, picks in real_picks_by_date.items():
        if len(picks) > 1:
            logger.warning(f"Multiple picks on {date}: {len(picks)} picks")
            
            # Sort by confidence (highest first)
            picks.sort(key=lambda x: float(x.get('confidence', 0)), reverse=True)
            
            # Keep the first (highest confidence) pick, mark others for deletion
            best_pick = picks[0]
            logger.info(f"  Keeping best pick: {best_pick.get('home_team')} vs {best_pick.get('away_team')} (confidence: {best_pick.get('confidence')})")
            
            for pick in picks[1:]:
                picks_to_delete.append(pick)
                logger.info(f"  Marking for deletion: {pick.get('home_team')} vs {pick.get('away_team')} (confidence: {pick.get('confidence')})")
    
    # Delete the extra picks
    if picks_to_delete:
        try:
            conn = get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            for pick in picks_to_delete:
                pick_id = pick.get('id')
                home_team = pick.get('home_team', 'N/A')
                away_team = pick.get('away_team', 'N/A')
                
                logger.warning(f"Deleting extra pick: {home_team} vs {away_team} (ID: {pick_id})")
                
                cursor.execute("DELETE FROM daily_picks WHERE id = ?", (pick_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.success(f"Deleted {len(picks_to_delete)} extra picks")
            
        except Exception as e:
            logger.error(f"Error deleting extra picks: {e}")

def main():
    """Main function to clean daily picks"""
    logger.info("Starting daily picks cleanup...")
    
    # Check current picks
    picks = check_current_picks()
    
    if not picks:
        logger.error("Could not retrieve picks from database")
        return
    
    # Display current picks
    logger.info(f"\n📊 CURRENT PICKS:")
    for i, pick in enumerate(picks, 1):
        logger.info(f"  {i}. {pick.get('home_team', 'N/A')} vs {pick.get('away_team', 'N/A')}")
        logger.info(f"     Prediction: {pick.get('prediction', 'N/A')}")
        logger.info(f"     Confidence: {pick.get('confidence', 'N/A')}")
        logger.info(f"     Created: {pick.get('created_at', 'N/A')}")
        logger.info(f"     ID: {pick.get('id', 'N/A')}")
    
    # Identify fake and real picks
    fake_picks, real_picks = identify_fake_picks(picks)
    
    logger.info(f"\n📊 ANALYSIS RESULTS:")
    logger.info(f"Total picks found: {len(picks)}")
    logger.info(f"Fake/imaginary picks: {len(fake_picks)}")
    logger.info(f"Real picks: {len(real_picks)}")
    
    if fake_picks:
        logger.warning(f"\n🚨 FAKE PICKS TO REMOVE:")
        for pick in fake_picks:
            logger.warning(f"  - {pick.get('home_team')} vs {pick.get('away_team')} (ID: {pick.get('id')})")
    
    # Group real picks by date
    real_picks_by_date = group_picks_by_date(real_picks)
    
    logger.info(f"\n📅 REAL PICKS BY DATE:")
    for date, date_picks in real_picks_by_date.items():
        logger.info(f"  {date}: {len(date_picks)} pick(s)")
        if len(date_picks) > 1:
            logger.warning(f"    ⚠️  Multiple picks on {date} - will keep only the best one")
    
    # Ask for confirmation
    logger.info(f"\n✅ CLEANUP PLAN:")
    logger.info(f"1. Remove {len(fake_picks)} fake/imaginary picks")
    logger.info(f"2. Keep only 1 real pick per day")
    logger.info(f"3. Final result: {len(real_picks_by_date)} picks (one per day)")
    
    # Perform cleanup
    logger.info(f"\n🧹 PERFORMING CLEANUP...")
    
    # Delete fake picks
    delete_fake_picks(fake_picks)
    
    # Keep only best pick per day
    keep_best_pick_per_day(real_picks_by_date)
    
    # Final check
    logger.info(f"\n✅ FINAL CHECK:")
    final_picks = check_current_picks()
    if final_picks:
        logger.success(f"Final picks count: {len(final_picks)}")
        for pick in final_picks:
            logger.info(f"  - {pick.get('home_team')} vs {pick.get('away_team')} (confidence: {pick.get('confidence')})")
    
    logger.success("Daily picks cleanup completed!")

if __name__ == "__main__":
    main() 