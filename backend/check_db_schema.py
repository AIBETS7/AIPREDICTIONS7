#!/usr/bin/env python3
"""
Check database schema to see what columns exist
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from loguru import logger

def check_db_schema():
    """Check the database schema"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'football_predictions.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(daily_picks)")
        columns = cursor.fetchall()
        
        logger.info("Database schema for daily_picks table:")
        for col in columns:
            logger.info(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - Default: {col[4]}")
        
        # Get sample data
        cursor.execute("SELECT * FROM daily_picks LIMIT 3")
        rows = cursor.fetchall()
        
        if rows:
            logger.info(f"\nSample data ({len(rows)} rows):")
            for i, row in enumerate(rows, 1):
                logger.info(f"  Row {i}: {row}")
        else:
            logger.info("No data found in daily_picks table")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error checking schema: {e}")

if __name__ == "__main__":
    check_db_schema() 