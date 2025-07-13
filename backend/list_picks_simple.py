#!/usr/bin/env python3
"""
Simple script to list all current picks
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from config.database import DATABASE_URL

def list_all_picks():
    """List all picks in the database"""
    print("Current picks in database:")
    print("=" * 50)
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, home_team, away_team, prediction, prediction_type, 
                       competition, match_time, created_at
                FROM daily_picks 
                ORDER BY created_at DESC
            """))
            
            picks = result.fetchall()
            
            for i, pick in enumerate(picks, 1):
                print(f"{i}. {pick['home_team']} vs {pick['away_team']}")
                print(f"   Prediction: {pick['prediction']} ({pick['prediction_type']})")
                print(f"   Competition: {pick['competition']}")
                print(f"   Match Time: {pick['match_time']}")
                print(f"   Created: {pick['created_at']}")
                print(f"   ID: {pick['id']}")
                print("-" * 30)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_all_picks() 