#!/usr/bin/env python3
"""
View current matches data collected from multiple sources
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from config.database import DATABASE_URL
from loguru import logger

def view_current_matches():
    """View the current matches data collected from all sources"""
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Get total count
            result = conn.execute(text("SELECT COUNT(*) as total FROM current_matches"))
            total = result.fetchone()['total']
            
            logger.info(f"📊 Total current matches in database: {total}")
            
            if total == 0:
                logger.info("No current matches found. This might be because:")
                logger.info("1. It's off-season for most leagues")
                logger.info("2. The websites are blocking automated access")
                logger.info("3. The match data structure has changed")
                return
            
            # Get data by source
            result = conn.execute(text("""
                SELECT source, COUNT(*) as count 
                FROM current_matches 
                GROUP BY source 
                ORDER BY count DESC
            """))
            
            logger.info("📈 Data by source:")
            for row in result:
                logger.info(f"   {row['source']}: {row['count']} matches")
            
            # Get data by league
            result = conn.execute(text("""
                SELECT league, COUNT(*) as count 
                FROM current_matches 
                GROUP BY league 
                ORDER BY count DESC
            """))
            
            logger.info("🏆 Data by league:")
            for row in result:
                logger.info(f"   {row['league']}: {row['count']} matches")
            
            # Show recent matches
            result = conn.execute(text("""
                SELECT home_team, away_team, home_score, away_score, 
                       match_time, league, source, created_at
                FROM current_matches 
                ORDER BY created_at DESC 
                LIMIT 15
            """))
            
            logger.info("🆕 Recent current matches:")
            for row in result:
                score = f"{row['home_score']}-{row['away_score']}" if row['home_score'] is not None else "TBD"
                time_info = f" ({row['match_time']})" if row['match_time'] else ""
                logger.info(f"   {row['home_team']} vs {row['away_team']} ({score}){time_info} - {row['league']} ({row['source']})")
            
            # Show matches with scores (completed matches)
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM current_matches 
                WHERE home_score IS NOT NULL AND away_score IS NOT NULL
            """))
            
            completed = result.fetchone()['count']
            logger.info(f"✅ Completed matches with scores: {completed}")
            
            # Show upcoming matches
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM current_matches 
                WHERE home_score IS NULL OR away_score IS NULL
            """))
            
            upcoming = result.fetchone()['count']
            logger.info(f"⏰ Upcoming/scheduled matches: {upcoming}")
            
            # Show matches by league with details
            result = conn.execute(text("""
                SELECT league, home_team, away_team, home_score, away_score, match_time, source
                FROM current_matches 
                ORDER BY league, created_at DESC
            """))
            
            logger.info("📋 All matches by league:")
            current_league = None
            for row in result:
                if current_league != row['league']:
                    current_league = row['league']
                    logger.info(f"\n🏆 {current_league}:")
                
                score = f"{row['home_score']}-{row['away_score']}" if row['home_score'] is not None else "TBD"
                time_info = f" ({row['match_time']})" if row['match_time'] else ""
                logger.info(f"   {row['home_team']} vs {row['away_team']} ({score}){time_info} - {row['source']}")
            
    except Exception as e:
        logger.error(f"Error viewing current matches data: {e}")

def search_team_matches(team_name):
    """Search for matches involving a specific team"""
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT home_team, away_team, home_score, away_score, 
                       match_time, league, source, created_at
                FROM current_matches 
                WHERE home_team ILIKE :team OR away_team ILIKE :team
                ORDER BY created_at DESC 
                LIMIT 20
            """), {'team': f'%{team_name}%'})
            
            matches = result.fetchall()
            
            if matches:
                logger.info(f"🔍 Current matches involving '{team_name}':")
                for row in matches:
                    score = f"{row['home_score']}-{row['away_score']}" if row['home_score'] is not None else "TBD"
                    time_info = f" ({row['match_time']})" if row['match_time'] else ""
                    logger.info(f"   {row['home_team']} vs {row['away_team']} ({score}){time_info} - {row['league']} ({row['source']})")
            else:
                logger.info(f"No current matches found for team '{team_name}'")
                
    except Exception as e:
        logger.error(f"Error searching team matches: {e}")

def main():
    logger.info("🔍 Viewing current football matches data...")
    
    # View overall statistics
    view_current_matches()
    
    # Search for specific teams if provided
    if len(sys.argv) > 1:
        team_name = sys.argv[1]
        logger.info(f"\n🔍 Searching for current matches involving '{team_name}'...")
        search_team_matches(team_name)

if __name__ == "__main__":
    main() 