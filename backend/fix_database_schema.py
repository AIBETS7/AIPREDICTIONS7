#!/usr/bin/env python3
"""
Fix database schema to include competition column
"""

import os
from sqlalchemy import create_engine, text
from config.database import DATABASE_URL

def fix_database_schema():
    """Add competition column to daily_picks table"""
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if competition column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'daily_picks' 
                AND column_name = 'competition'
            """))
            
            if not result.fetchone():
                # Add competition column
                conn.execute(text("ALTER TABLE daily_picks ADD COLUMN competition VARCHAR"))
                print("✅ Added 'competition' column to daily_picks table")
            else:
                print("✅ 'competition' column already exists")
            
            # Commit the changes
            conn.commit()
            
    except Exception as e:
        print(f"❌ Error fixing database schema: {e}")

if __name__ == "__main__":
    fix_database_schema() 