#!/usr/bin/env python3
"""
Test Pick for Tonight at 9 PM
Fetches a real football match for today from API-Football and sends the pick to website and Telegram
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import create_engine, Table, Column, String, Float, DateTime, MetaData
import requests
import pytz
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger.add(
    "logs/football_predictions.log",
    level="INFO",
    format="{time} | {level} | {message}",
    rotation="1 day",
    retention="7 days"
)

API_KEY = "dc7adf0a857be5ca3fd75d79e82c69cb"
SPAIN_TZ = pytz.timezone('Europe/Madrid')


def fetch_tonight_match():
    today = datetime.now(SPAIN_TZ).strftime('%Y-%m-%d')
    url = f"https://v3.football.api-sports.io/fixtures?date={today}"
    headers = {"x-apisports-key": API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    matches = []
    for fixture in data.get("response", []):
        home = fixture["teams"]["home"]["name"]
        away = fixture["teams"]["away"]["name"]
        league = fixture["league"]["name"]
        utc_time = fixture["fixture"]["date"]
        # Convert UTC to Spain time
        match_time_utc = datetime.fromisoformat(utc_time.replace('Z', '+00:00'))
        match_time_spain = match_time_utc.astimezone(SPAIN_TZ)
        matches.append({
            "home": home,
            "away": away,
            "league": league,
            "match_time": match_time_spain,
            "fixture_id": fixture["fixture"]["id"]
        })
    # Find match at or after 21:00 Spain time
    nine_pm = datetime.now(SPAIN_TZ).replace(hour=21, minute=0, second=0, microsecond=0)
    after_nine = [m for m in matches if m["match_time"] >= nine_pm]
    if after_nine:
        return after_nine[0]
    elif matches:
        return matches[-1]  # fallback: last match of the day
    else:
        return None

def create_test_pick():
    match = fetch_tonight_match()
    if not match:
        logger.error("No matches found for today!")
        return
    test_pick = {
        'id': str(uuid.uuid4()),
        'match_id': str(match['fixture_id']),
        'home_team': match['home'],
        'away_team': match['away'],
        'match_time': match['match_time'].strftime('%Y-%m-%d %H:%M'),
        'prediction_type': 'Match Winner',
        'prediction': match['home'],  # Simple: pick home team
        'confidence': 70.0,
        'odds': 1.80,
        'reasoning': f"{match['home']} has a strong home record. This is an automated test pick.",
        'tipster': 'AI Predictor Pro',
        'created_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(hours=3)).isoformat()
    }
    # Save to database
    engine = create_engine('sqlite:///football_predictions.db')
    metadata = MetaData()
    picks_table = Table('daily_picks', metadata,
        Column('id', String, primary_key=True),
        Column('match_id', String),
        Column('home_team', String),
        Column('away_team', String),
        Column('match_time', String),
        Column('prediction_type', String),
        Column('prediction', String),
        Column('confidence', Float),
        Column('odds', Float),
        Column('reasoning', String),
        Column('tipster', String),
        Column('created_at', String),
        Column('expires_at', String)
    )
    with engine.begin() as conn:
        conn.execute(picks_table.insert().prefix_with('OR REPLACE'), test_pick)
    logger.info(f"Test pick created: {test_pick['home_team']} vs {test_pick['away_team']}")
    
    # Save to JSON file for website
    picks_data = {
        'current_pick': test_pick,
        'recent_picks': [test_pick],
        'last_updated': datetime.now().isoformat()
    }
    
    # Ensure the directory exists
    os.makedirs('data/processed', exist_ok=True)
    
    with open('data/processed/latest_data.json', 'w') as f:
        json.dump(picks_data, f, indent=2)
    logger.info("Pick saved to website JSON file")
    
    # Send to Telegram
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if telegram_token and chat_id:
        message = f"""
🎯 **TONIGHT'S PREMIUM PICK** 🎯

⚽ **{test_pick['home_team']} vs {test_pick['away_team']}**
🏆 **{match['league']}**
⏰ **{test_pick['match_time']}**

💡 **Prediction:** {test_pick['prediction']}
🎯 **Pick Type:** {test_pick['prediction_type']}
📊 **Confidence:** {test_pick['confidence']}%
💰 **Odds:** {test_pick['odds']}
💶 **Stake:** €100

📝 **Analysis:**
{test_pick['reasoning']}

🔒 **Premium Pick - Unlock with subscription**
        """
        try:
            response = requests.post(
                f'https://api.telegram.org/bot{telegram_token}/sendMessage',
                json={
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'Markdown'
                }
            )
            if response.status_code == 200:
                logger.info("Telegram message sent successfully")
                print("✅ Telegram message sent successfully!")
            else:
                logger.error(f"Failed to send Telegram message: {response.text}")
                print(f"❌ Failed to send Telegram message: {response.text}")
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            print(f"❌ Error sending Telegram message: {e}")
    else:
        logger.warning("Telegram credentials not found")
        print("⚠️ Telegram credentials not found in .env file")
    
    return test_pick

if __name__ == "__main__":
    create_test_pick() 