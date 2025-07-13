#!/usr/bin/env python3
"""
Delete all picks from the daily_picks table
"""
from sqlalchemy import create_engine, text
from config.database import DATABASE_URL

def delete_all_picks():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM daily_picks"))
        print("All picks have been deleted from the daily_picks table.")

if __name__ == "__main__":
    delete_all_picks() 