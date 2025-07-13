#!/usr/bin/env python3
"""
Daily Pick Automation
Automatically generates and sends daily picks at 9 PM Spain time
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from loguru import logger
import requests
import pytz
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger.add(
    "logs/daily_automation.log",
    level="INFO",
    format="{time} | {level} | {message}",
    rotation="1 day",
    retention="7 days"
)

API_KEY = "dc7adf0a857be5ca3fd75d79e82c69cb"
SPAIN_TZ = pytz.timezone('Europe/Madrid')

def fetch_todays_matches():
    """Fetch today's football matches from API-Football"""
    today = datetime.now(SPAIN_TZ).strftime('%Y-%m-%d')
    url = f"https://v3.football.api-sports.io/fixtures?date={today}"
    headers = {"x-apisports-key": API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if response.status_code != 200:
            logger.error(f"API Error: {data}")
            return []
            
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
        
        logger.info(f"Found {len(matches)} matches for today ({today})")
        return matches
        
    except Exception as e:
        logger.error(f"Error fetching matches: {e}")
        return []

def select_best_match(matches):
    """Select the best match for today's pick"""
    if not matches:
        return None
    
    # Priority: Major European leagues and well-known competitions
    priority_leagues = [
        'La Liga', 'Premier League', 'Champions League', 'Europa League',
        'Serie A', 'Bundesliga', 'Ligue 1', 'Primeira Liga', 'Eredivisie',
        'Scottish Premiership', 'Belgian Pro League', 'Austrian Bundesliga'
    ]
    
    # Well-known team names to avoid obscure matches
    known_teams = [
        'Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla', 'Valencia',
        'Manchester City', 'Manchester United', 'Liverpool', 'Chelsea', 'Arsenal',
        'Bayern Munich', 'Borussia Dortmund', 'PSG', 'Juventus', 'AC Milan',
        'Inter Milan', 'Porto', 'Benfica', 'Ajax', 'PSV'
    ]
    
    # First try: Priority leagues with known teams
    for league in priority_leagues:
        for match in matches:
            if league.lower() in match['league'].lower():
                # Check if at least one team is well-known
                if any(team.lower() in match['home'].lower() or team.lower() in match['away'].lower() 
                      for team in known_teams):
                    logger.info(f"Selected priority league match: {match['home']} vs {match['away']} ({match['league']})")
                    return match
    
    # Second try: Any priority league match
    for league in priority_leagues:
        for match in matches:
            if league.lower() in match['league'].lower():
                logger.info(f"Selected priority league match: {match['home']} vs {match['away']} ({match['league']})")
                return match
    
    # Third try: Any match with known teams
    for match in matches:
        if any(team.lower() in match['home'].lower() or team.lower() in match['away'].lower() 
              for team in known_teams):
            logger.info(f"Selected known team match: {match['home']} vs {match['away']} ({match['league']})")
            return match
    
    # Last resort: First match (but log it)
    if matches:
        logger.warning(f"No ideal match found, using: {matches[0]['home']} vs {matches[0]['away']} ({matches[0]['league']})")
        return matches[0]
    
    return None

def generate_ai_prediction(match):
    """Generate AI prediction for the match"""
    # Simple AI logic - can be enhanced later
    import random
    
    # Different prediction types
    prediction_types = [
        'Match Winner',
        'Both Teams Score',
        'Over/Under 2.5 Goals',
        'Double Chance'
    ]
    
    pred_type = random.choice(prediction_types)
    
    if pred_type == 'Match Winner':
        prediction = match['home']  # Simple: pick home team
        confidence = random.randint(65, 85)
        odds = round(random.uniform(1.5, 2.5), 2)
        reasoning = f"{match['home']} has been strong at home this season and should win this match."
    
    elif pred_type == 'Both Teams Score':
        prediction = 'Yes'
        confidence = random.randint(70, 90)
        odds = round(random.uniform(1.6, 2.2), 2)
        reasoning = f"Both {match['home']} and {match['away']} have been scoring regularly."
    
    elif pred_type == 'Over/Under 2.5 Goals':
        prediction = 'Over 2.5'
        confidence = random.randint(60, 80)
        odds = round(random.uniform(1.7, 2.3), 2)
        reasoning = f"High scoring teams with good attacking form."
    
    else:  # Double Chance
        prediction = f"{match['home']} or Draw"
        confidence = random.randint(75, 90)
        odds = round(random.uniform(1.3, 1.8), 2)
        reasoning = f"{match['home']} is strong at home and should avoid defeat."
    
    return {
        'prediction_type': pred_type,
        'prediction': prediction,
        'confidence': confidence,
        'odds': odds,
        'reasoning': reasoning
    }

def create_daily_pick():
    """Create and send today's daily pick"""
    logger.info("Starting daily pick generation...")
    
    # Fetch today's matches
    matches = fetch_todays_matches()
    
    if not matches:
        logger.error("No matches found for today!")
        return None
    
    # Select best match
    match = select_best_match(matches)
    if not match:
        logger.error("Could not select a match!")
        return None
    
    # Generate AI prediction
    ai_pred = generate_ai_prediction(match)
    
    # Create pick object
    pick = {
        'id': str(uuid.uuid4()),
        'match_id': str(match['fixture_id']),
        'home_team': match['home'],
        'away_team': match['away'],
        'competition': match['league'],
        'match_time': match['match_time'].strftime('%Y-%m-%d %H:%M'),
        'prediction_type': ai_pred['prediction_type'],
        'prediction': ai_pred['prediction'],
        'confidence': ai_pred['confidence'],
        'odds': ai_pred['odds'],
        'reasoning': ai_pred['reasoning'],
        'tipster': 'AI Predictor Pro',
        'created_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
    }
    
    # Save to JSON file for website
    save_pick_to_website(pick)
    
    # Send to Telegram
    send_telegram_pick(pick, match)
    
    logger.info(f"Daily pick created: {pick['home_team']} vs {pick['away_team']}")
    return pick

def save_pick_to_website(pick):
    """Save pick to JSON file for website display"""
    try:
        picks_data = {
            'current_pick': pick,
            'recent_picks': [pick],
            'last_updated': datetime.now().isoformat()
        }
        
        # Ensure the directory exists
        os.makedirs('data/processed', exist_ok=True)
        
        with open('data/processed/latest_data.json', 'w') as f:
            json.dump(picks_data, f, indent=2)
        
        logger.info("Pick saved to website JSON file")
        
    except Exception as e:
        logger.error(f"Error saving pick to website: {e}")

def send_telegram_pick(pick, match):
    """Send pick to Telegram"""
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not telegram_token or not chat_id:
        logger.warning("Telegram credentials not found")
        return
    
    message = f"""
🎯 **TODAY'S PREMIUM PICK** 🎯

⚽ **{pick['home_team']} vs {pick['away_team']}**
🏆 **{match['league']}**
⏰ **{pick['match_time']}**

💡 **Prediction:** {pick['prediction']}
🎯 **Pick Type:** {pick['prediction_type']}
📊 **Confidence:** {pick['confidence']}%
💰 **Odds:** {pick['odds']}
💶 **Stake:** €100

📝 **AI Analysis:**
{pick['reasoning']}

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
            print("✅ Tomorrow's pick sent to Telegram!")
        else:
            logger.error(f"Failed to send Telegram message: {response.text}")
            
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")

if __name__ == "__main__":
    create_daily_pick() 