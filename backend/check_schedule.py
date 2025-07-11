#!/usr/bin/env python3
"""
Check upcoming matches and automation schedule
"""

import os
from datetime import datetime, timedelta
from loguru import logger
from config.settings import LOGGING_CONFIG
from data_collector import DataCollector

# Configure logging
logger.add(
    LOGGING_CONFIG['file'],
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format'],
    rotation=LOGGING_CONFIG['rotation'],
    retention=LOGGING_CONFIG['retention']
)

def check_schedule():
    """Check upcoming matches and automation schedule"""
    print("=" * 60)
    print("FOOTBALL PREDICTIONS AUTOMATION SCHEDULE")
    print("=" * 60)
    
    # Show automation schedule
    print("\n🤖 AUTOMATION SCHEDULE:")
    print("• Runs twice daily:")
    print("  - 08:00 UTC (4:00 AM EST / 1:00 AM PST)")
    print("  - 18:00 UTC (2:00 PM EST / 11:00 AM PST)")
    print("• Only sends picks when there are upcoming matches")
    print("• Skips days with no games")
    
    # Check for upcoming matches
    print("\n📅 CHECKING UPCOMING MATCHES:")
    try:
        collector = DataCollector()
        data = collector.get_latest_data()
        
        upcoming_matches = [
            match for match in data.get('matches', [])
            if match.get('status') == 'scheduled'
        ]
        
        if not upcoming_matches:
            print("❌ No upcoming matches found")
            print("   → Automation will skip today")
        else:
            print(f"✅ Found {len(upcoming_matches)} upcoming matches:")
            for i, match in enumerate(upcoming_matches[:5], 1):
                home = match.get('home_team', 'Unknown')
                away = match.get('away_team', 'Unknown')
                time = match.get('time', 'TBD')
                print(f"   {i}. {home} vs {away} - {time}")
            
            if len(upcoming_matches) > 5:
                print(f"   ... and {len(upcoming_matches) - 5} more matches")
            print("   → Automation will generate picks today")
    
    except Exception as e:
        print(f"❌ Error checking matches: {e}")
        print("   → Automation will skip today")
    
    # Show next run times
    print("\n⏰ NEXT AUTOMATION RUNS:")
    now = datetime.utcnow()
    
    # Morning run (8:00 UTC)
    morning_run = now.replace(hour=8, minute=0, second=0, microsecond=0)
    if now.hour >= 8:
        morning_run += timedelta(days=1)
    
    # Evening run (18:00 UTC)
    evening_run = now.replace(hour=18, minute=0, second=0, microsecond=0)
    if now.hour >= 18:
        evening_run += timedelta(days=1)
    
    print(f"• Morning: {morning_run.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"• Evening: {evening_run.strftime('%Y-%m-%d %H:%M UTC')}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_schedule() 