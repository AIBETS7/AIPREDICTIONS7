#!/usr/bin/env python3
"""
Add result tracking fields to database schema
"""

import os
from sqlalchemy import create_engine, text
from config.database import DATABASE_URL

def add_result_tracking():
    """Add result tracking fields to daily_picks table"""
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if result_status column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'daily_picks' 
                AND column_name = 'result_status'
            """))
            
            if not result.fetchone():
                # Add result_status column
                conn.execute(text("ALTER TABLE daily_picks ADD COLUMN result_status VARCHAR DEFAULT 'pending'"))
                print("✅ Added 'result_status' column to daily_picks table")
            else:
                print("✅ 'result_status' column already exists")
            
            # Check if actual_result column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'daily_picks' 
                AND column_name = 'actual_result'
            """))
            
            if not result.fetchone():
                # Add actual_result column
                conn.execute(text("ALTER TABLE daily_picks ADD COLUMN actual_result VARCHAR"))
                print("✅ Added 'actual_result' column to daily_picks table")
            else:
                print("✅ 'actual_result' column already exists")
            
            # Check if result_updated_at column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'daily_picks' 
                AND column_name = 'result_updated_at'
            """))
            
            if not result.fetchone():
                # Add result_updated_at column
                conn.execute(text("ALTER TABLE daily_picks ADD COLUMN result_updated_at TIMESTAMP"))
                print("✅ Added 'result_updated_at' column to daily_picks table")
            else:
                print("✅ 'result_updated_at' column already exists")
            
            # Commit the changes
            conn.commit()
            
    except Exception as e:
        print(f"❌ Error adding result tracking: {e}")

if __name__ == "__main__":
    add_result_tracking() 