#!/usr/bin/env python3
"""
Script to add test picks to the database for demonstration
"""

import sys
import os
from datetime import datetime, timedelta
import psycopg
import uuid

# Add backend directory to path
sys.path.append('backend')
from config.database import DATABASE_URL

def get_db_connection():
    """Create a database connection using the DATABASE_URL from settings"""
    try:
        # Parse the DATABASE_URL to get connection parameters
        if DATABASE_URL.startswith('postgresql://'):
            # Remove the postgresql:// prefix
            url = DATABASE_URL.replace('postgresql://', '')
            
            # Split into user:password@host:port/database
            if '@' in url:
                credentials, rest = url.split('@')
                user, password = credentials.split(':')
                
                # Handle host:port/database?params
                if '/' in rest:
                    host_port, database_with_params = rest.split('/', 1)
                    # Remove query parameters from database name
                    database = database_with_params.split('?')[0]
                    
                    if ':' in host_port:
                        host, port = host_port.split(':')
                    else:
                        host, port = host_port, '5432'
                    
                    conn = psycopg.connect(
                        host=host,
                        port=port,
                        dbname=database,
                        user=user,
                        password=password,
                        sslmode='require'
                    )
                    return conn
        else:
            print(f"Unsupported database URL format: {DATABASE_URL}")
            return None
            
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def add_test_picks():
    """Add a Women's Euro pick for Italy Fem vs Spain Fem for today"""
    from datetime import datetime, timedelta
    test_picks = [
        {
            'id': str(uuid.uuid4()),
            'home_team': 'Italy Fem',
            'away_team': 'Spain Fem',
            'prediction': 'Spain Fem Win',
            'prediction_type': 'match_winner',
            'confidence': 85,
            'odds': 1.95,
            'stake': 50,
            'reasoning': 'Spain Fem have won their last 5 matches and have a stronger squad. Italy Fem have struggled defensively in recent games.',
            'match_time': (datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)),
            'competition': "Women's Euro",
            'tipster': 'AI Tipster'
        }
    ]
    try:
        conn = get_db_connection()
        if not conn:
            print("Failed to connect to database")
            return
        cursor = conn.cursor()
        for pick in test_picks:
            query = """
            INSERT INTO daily_picks 
            (id, home_team, away_team, prediction, prediction_type, confidence, odds, stake, reasoning, match_time, competition, tipster, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                pick['id'],
                pick['home_team'],
                pick['away_team'],
                pick['prediction'],
                pick['prediction_type'],
                pick['confidence'],
                pick['odds'],
                pick['stake'],
                pick['reasoning'],
                pick['match_time'],
                pick['competition'],
                pick['tipster'],
                datetime.now()
            ))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Successfully added Women's Euro pick for Italy Fem vs Spain Fem!")
        print("You can now view it on your website at http://localhost:8000")
    except Exception as e:
        print(f"Error adding test picks: {e}")

def print_all_picks():
    try:
        conn = get_db_connection()
        if not conn:
            print("Failed to connect to database")
            return
        cursor = conn.cursor()
        cursor.execute("SELECT id, home_team, away_team, prediction, match_time, created_at, competition FROM daily_picks ORDER BY created_at DESC LIMIT 10;")
        rows = cursor.fetchall()
        print("Last 10 picks in the database:")
        for row in rows:
            print(row)
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error reading picks: {e}")

if __name__ == '__main__':
    add_test_picks()
    print_all_picks() 