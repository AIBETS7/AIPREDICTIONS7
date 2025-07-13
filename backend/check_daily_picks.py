#!/usr/bin/env python3
"""
Check and clean up daily picks
Remove fake/imaginary picks and ensure only one real pick per day
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import create_engine, text
from config.database import DATABASE_URL
import json
from dateutil.parser import parse as parse_date

def check_current_picks():
    """Check all current daily picks"""
    logger.info("Checking current daily picks...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Get all picks ordered by creation date
            result = conn.execute(text("""
                SELECT id, home_team, away_team, prediction, prediction_type, 
                       confidence, odds, match_time, reasoning, tipster, 
                       created_at, result_status, actual_result, competition
                FROM daily_picks 
                ORDER BY created_at DESC
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
                    'match_time': row[7],
                    'reasoning': row[8],
                    'tipster': row[9],
                    'created_at': row[10],
                    'result_status': row[11] or 'pending',
                    'actual_result': row[12],
                    'competition': row[13]
                })
            
            logger.info(f"Found {len(picks)} total picks")
            
            # Group by date
            picks_by_date = {}
            for pick in picks:
                if pick['created_at']:
                    if isinstance(pick['created_at'], str):
                        try:
                            dt = parse_date(pick['created_at'])
                        except Exception:
                            logger.error(f"Could not parse date: {pick['created_at']}")
                            continue
                    else:
                        dt = pick['created_at']
                    date_key = dt.date()
                    if date_key not in picks_by_date:
                        picks_by_date[date_key] = []
                    picks_by_date[date_key].append(pick)
            
            # Analyze each date
            for date, date_picks in picks_by_date.items():
                logger.info(f"\n=== {date} ===")
                logger.info(f"Picks on this date: {len(date_picks)}")
                
                for i, pick in enumerate(date_picks, 1):
                    logger.info(f"{i}. {pick['home_team']} vs {pick['away_team']}")
                    logger.info(f"   Prediction: {pick['prediction']} ({pick['prediction_type']})")
                    logger.info(f"   Competition: {pick['competition']}")
                    logger.info(f"   Match time: {pick['match_time']}")
                    logger.info(f"   Result: {pick['result_status']} - {pick['actual_result']}")
                    logger.info(f"   ID: {pick['id']}")
                    
                    # Check if this looks like a real pick
                    is_real = check_if_real_pick(pick)
                    if is_real:
                        logger.info("   ✅ Looks like a real pick")
                    else:
                        logger.info("   ❌ Looks like a fake/imaginary pick")
                    logger.info("")
            
            return picks_by_date
            
    except Exception as e:
        logger.error(f"Error checking picks: {e}")
        return {}

def check_if_real_pick(pick):
    """Check if a pick looks real or fake"""
    # Real picks should have:
    # 1. Real team names (not test data)
    # 2. Real competition names
    # 3. Real match times
    # 4. Proper reasoning
    
    fake_indicators = [
        'test' in pick['id'].lower(),
        'test' in pick['home_team'].lower(),
        'test' in pick['away_team'].lower(),
        'barcelona' in pick['home_team'].lower() and 'real madrid' in pick['away_team'].lower(),  # Classic test matchup
        'real madrid' in pick['home_team'].lower() and 'barcelona' in pick['away_team'].lower(),  # Classic test matchup
        pick['competition'] and 'test' in pick['competition'].lower(),
        pick['reasoning'] and 'test' in pick['reasoning'].lower(),
        pick['tipster'] and 'test' in pick['tipster'].lower(),
    ]
    
    return not any(fake_indicators)

def identify_fake_picks(picks_by_date):
    """Identify which picks are fake and should be removed"""
    fake_picks = []
    
    for date, date_picks in picks_by_date.items():
        logger.info(f"\nAnalyzing {date}:")
        
        # Find fake picks
        date_fake_picks = [pick for pick in date_picks if not check_if_real_pick(pick)]
        
        if date_fake_picks:
            logger.info(f"Found {len(date_fake_picks)} fake picks to remove:")
            for pick in date_fake_picks:
                logger.info(f"  - {pick['id']}: {pick['home_team']} vs {pick['away_team']}")
                fake_picks.extend(date_fake_picks)
        else:
            logger.info("No fake picks found")
        
        # Check for multiple picks per day
        real_picks = [pick for pick in date_picks if check_if_real_pick(pick)]
        if len(real_picks) > 1:
            logger.warning(f"⚠️ Found {len(real_picks)} real picks on {date}. Should keep only the most recent one.")
            # Keep only the most recent real pick
            real_picks.sort(key=lambda x: x['created_at'], reverse=True)
            picks_to_remove = real_picks[1:]  # All except the first (most recent)
            logger.info(f"Will remove {len(picks_to_remove)} older picks:")
            for pick in picks_to_remove:
                logger.info(f"  - {pick['id']}: {pick['home_team']} vs {pick['away_team']}")
            fake_picks.extend(picks_to_remove)
    
    return fake_picks

def remove_fake_picks(fake_picks):
    """Remove fake picks from database"""
    if not fake_picks:
        logger.info("No fake picks to remove")
        return
    
    logger.info(f"\nRemoving {len(fake_picks)} fake/duplicate picks...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            for pick in fake_picks:
                logger.info(f"Removing: {pick['id']} - {pick['home_team']} vs {pick['away_team']}")
                conn.execute(text("DELETE FROM daily_picks WHERE id = :id"), {'id': pick['id']})
            
            logger.info("✅ Fake picks removed successfully")
            
    except Exception as e:
        logger.error(f"Error removing fake picks: {e}")

def cleanup_to_one_real_pick():
    """Keep only the Real Madrid vs Barcelona pick for 2025-07-13T21:00:00 and delete all others"""
    from sqlalchemy import create_engine, text
    from config.database import DATABASE_URL
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Find the ID of the real pick to keep
        result = conn.execute(text("""
            SELECT id FROM daily_picks
            WHERE home_team = 'Real Madrid' AND away_team = 'Barcelona'
              AND match_time LIKE '2025-07-13%'
            LIMIT 1
        """))
        row = result.fetchone()
        if not row:
            print("No valid Real Madrid vs Barcelona pick found for 2025-07-13.")
            return
        keep_id = row['id']
        # Delete all other picks
        conn.execute(text("""
            DELETE FROM daily_picks WHERE id != :keep_id
        """), {"keep_id": keep_id})
        print(f"Kept pick {keep_id} and deleted all others.")

def delete_all_picks():
    """Delete all picks from the daily_picks table"""
    from sqlalchemy import create_engine, text
    from config.database import DATABASE_URL
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM daily_picks"))
        print("All picks have been deleted from the daily_picks table.")

def main():
    """Main function"""
    logger.info("Starting daily picks cleanup...")
    
    # Check current picks
    picks_by_date = check_current_picks()
    
    if not picks_by_date:
        logger.info("No picks found")
        return
    
    # Identify fake picks
    fake_picks = identify_fake_picks(picks_by_date)
    
    if fake_picks:
        # Ask for confirmation
        response = input(f"\nFound {len(fake_picks)} picks to remove. Continue? (y/N): ")
        if response.lower() == 'y':
            remove_fake_picks(fake_picks)
        else:
            logger.info("Cleanup cancelled")
    else:
        logger.info("No fake picks found. Database is clean!")

if __name__ == "__main__":
    # Uncomment the next line to delete all picks
    delete_all_picks()
    # check_current_picks()
    # cleanup_to_one_real_pick() 