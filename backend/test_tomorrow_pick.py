#!/usr/bin/env python3
"""
Test script to verify tomorrow's pick generation
"""

import os
import sys
from datetime import datetime, timedelta
from loguru import logger

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from daily_pick_automated import AutomatedDailyPickGenerator

def test_tomorrow_pick():
    """Test the pick generation for tomorrow"""
    print("🧪 Testing tomorrow's pick generation...")
    
    # Configure logging
    logger.add(
        "logs/test_tomorrow_pick.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation="1 day",
        retention="7 days"
    )
    
    generator = AutomatedDailyPickGenerator()
    
    # Get tomorrow's date
    tomorrow = datetime.now() + timedelta(days=1)
    print(f"📅 Testing for date: {tomorrow.strftime('%Y-%m-%d')}")
    
    # Generate pick without sending to Telegram
    pick = generator.generate_daily_pick(tomorrow)
    
    if pick.get('type') == 'no_pick':
        print("❌ No pick found for tomorrow")
        print(f"Reason: {pick['reason']}")
        return False
    else:
        match = pick['match']
        print("✅ Pick generated successfully!")
        print(f"🏆 Match: {match['home_team']} vs {match['away_team']}")
        print(f"🌍 Competition: {match['competition']}")
        print(f"⏰ Time: {match['time'].strftime('%H:%M')} - {match['time'].strftime('%d/%m/%Y')}")
        print(f"📊 Market: {pick['market']}")
        print(f"💰 Odds: {pick['odds']}")
        print(f"📈 Probability: {pick['probability']:.1f}%")
        print(f"🎯 Confidence: {pick['confidence']:.1f}%")
        print(f"🔍 Source: {match['source']}")
        print(f"✅ Real Match: {match['is_real']}")
        
        return True

if __name__ == "__main__":
    success = test_tomorrow_pick()
    if success:
        print("\n🎉 Test completed successfully! The system is ready for tomorrow.")
    else:
        print("\n⚠️ Test completed with issues. Please check the configuration.") 