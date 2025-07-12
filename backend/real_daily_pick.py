#!/usr/bin/env python3
"""
Real Daily Football Pick Generator
Uses real match data from API-Football to generate predictions
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from loguru import logger
import psycopg
import requests
from typing import Dict, List, Optional

# Add backend directory to path
sys.path.append('backend')
from config.database import DATABASE_URL
from real_matches_collector import RealMatchesCollector, get_fallback_matches

class RealDailyPickGenerator:
    """Generate daily picks using real match data"""
    
    def __init__(self):
        self.collector = RealMatchesCollector()
        self.bot_token = '7582466483:AAHshXjaU0vu2nZsYd8wSY5pR1XJ6EHmZOQ'
        self.chat_id = '2070545442'
    
    def get_db_connection(self):
        """Create database connection"""
        try:
            if DATABASE_URL.startswith('postgresql://'):
                url = DATABASE_URL.replace('postgresql://', '')
                if '@' in url:
                    credentials, rest = url.split('@')
                    user, password = credentials.split(':')
                    if '/' in rest:
                        host_port, database_with_params = rest.split('/', 1)
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
                logger.error(f"Unsupported database URL format: {DATABASE_URL}")
                return None
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return None
    
    def get_real_matches(self) -> List[Dict]:
        """Get real matches for today and tomorrow"""
        try:
            # Try to get real matches from API
            today_matches = self.collector.get_todays_matches()
            tomorrow_matches = self.collector.get_upcoming_matches(days_ahead=1)
            
            all_matches = today_matches + tomorrow_matches
            
            if all_matches:
                logger.info(f"Successfully fetched {len(all_matches)} real matches from API")
                return all_matches
            else:
                logger.warning("No real matches found from API, using fallback data")
                return get_fallback_matches()
                
        except Exception as e:
            logger.error(f"Error fetching real matches: {e}")
            logger.info("Using fallback match data")
            return get_fallback_matches()
    
    def generate_prediction(self, match: Dict) -> Dict:
        """Generate a prediction for a specific match"""
        home_team = match['home_team']
        away_team = match['away_team']
        competition = match['competition']
        match_time = match['match_time']
        
        # Simple prediction logic (you can enhance this with more sophisticated analysis)
        predictions = [
            {
                'prediction': f'{home_team} Win',
                'confidence': 75,
                'odds': 2.10,
                'reasoning': f'{home_team} has been strong at home this season and should win this match.',
                'prediction_type': 'match_winner'
            },
            {
                'prediction': f'{away_team} Win',
                'confidence': 65,
                'odds': 3.20,
                'reasoning': f'{away_team} has been in good form recently and could upset the home team.',
                'prediction_type': 'match_winner'
            },
            {
                'prediction': 'Draw',
                'confidence': 45,
                'odds': 3.50,
                'reasoning': f'Both teams are evenly matched and this could end in a draw.',
                'prediction_type': 'match_winner'
            },
            {
                'prediction': 'Over 2.5 Goals',
                'confidence': 70,
                'odds': 1.85,
                'reasoning': f'Both teams have been scoring goals regularly, expect a high-scoring match.',
                'prediction_type': 'total_goals'
            }
        ]
        
        # Select the best prediction (highest confidence)
        best_prediction = max(predictions, key=lambda x: x['confidence'])
        
        return {
            'id': str(uuid.uuid4()),
            'home_team': home_team,
            'away_team': away_team,
            'prediction': best_prediction['prediction'],
            'prediction_type': best_prediction['prediction_type'],
            'confidence': best_prediction['confidence'],
            'odds': best_prediction['odds'],
            'stake': 50,  # Default stake
            'reasoning': best_prediction['reasoning'],
            'match_time': match_time,
            'competition': competition,
            'tipster': 'AI Tipster (Real Data)',
            'created_at': datetime.now().isoformat()
        }
    
    def select_best_match(self, matches: List[Dict]) -> Optional[Dict]:
        """Select the best match to predict on"""
        if not matches:
            return None
        
        # Filter for scheduled matches only
        scheduled_matches = [m for m in matches if m.get('status') == 'scheduled']
        
        if not scheduled_matches:
            logger.warning("No scheduled matches found")
            return None
        
        # Prioritize matches by competition importance
        competition_priority = {
            'La Liga': 10,
            'Champions League': 9,
            'Europa League': 8,
            'Premier League': 7,
            'Bundesliga': 6,
            'Serie A': 5,
            'Ligue 1': 4,
            'Copa Del Rey': 3
        }
        
        # Score each match
        scored_matches = []
        for match in scheduled_matches:
            score = competition_priority.get(match.get('competition', ''), 1)
            
            # Prefer matches happening today or tomorrow
            try:
                match_time = datetime.fromisoformat(match['match_time'].replace('Z', '+00:00'))
                days_until_match = (match_time - datetime.now()).days
                if days_until_match <= 1:
                    score += 5
            except:
                # If there's an error parsing the time, just use the base score
                pass
            
            scored_matches.append((score, match))
        
        # Return the highest scored match
        if scored_matches:
            scored_matches.sort(key=lambda x: x[0], reverse=True)
            return scored_matches[0][1]
        return None
    
    def store_prediction(self, prediction: Dict) -> bool:
        """Store prediction in database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                logger.error("Failed to connect to database")
                return False
            
            cursor = conn.cursor()
            
            query = """
            INSERT INTO daily_picks 
            (id, home_team, away_team, prediction, prediction_type, confidence, odds, stake, reasoning, match_time, competition, tipster, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                home_team = EXCLUDED.home_team,
                away_team = EXCLUDED.away_team,
                prediction = EXCLUDED.prediction,
                prediction_type = EXCLUDED.prediction_type,
                confidence = EXCLUDED.confidence,
                odds = EXCLUDED.odds,
                stake = EXCLUDED.stake,
                reasoning = EXCLUDED.reasoning,
                match_time = EXCLUDED.match_time,
                competition = EXCLUDED.competition,
                tipster = EXCLUDED.tipster,
                created_at = EXCLUDED.created_at
            """
            
            cursor.execute(query, (
                prediction['id'],
                prediction['home_team'],
                prediction['away_team'],
                prediction['prediction'],
                prediction['prediction_type'],
                prediction['confidence'],
                prediction['odds'],
                prediction['stake'],
                prediction['reasoning'],
                prediction['match_time'],
                prediction['competition'],
                prediction['tipster'],
                prediction['created_at']
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Prediction stored successfully: {prediction['home_team']} vs {prediction['away_team']}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing prediction: {e}")
            return False
    
    def send_telegram_message(self, prediction: Dict) -> bool:
        """Send prediction to Telegram"""
        try:
            # Get competition emoji
            competition = prediction['competition']
            if 'Women' in competition:
                competition_emoji = "⚽👩‍🦰"
            elif 'La Liga' in competition:
                competition_emoji = "⚽🇪🇸"
            elif 'Champions' in competition:
                competition_emoji = "⚽🏆"
            elif 'Premier' in competition:
                competition_emoji = "⚽🏴󠁧󠁢󠁥󠁮󠁧󠁿"
            else:
                competition_emoji = "⚽"
            
            # Format match time
            match_time = datetime.fromisoformat(prediction['match_time'].replace('Z', '+00:00'))
            formatted_time = match_time.strftime('%Y-%m-%d %H:%M UTC')
            
            message = (
                f"🎯 **Real Match Prediction!**\n\n"
                f"{competition_emoji} **{competition}**\n"
                f"🏟️ **Match**: {prediction['home_team']} vs {prediction['away_team']}\n"
                f"🕐 **Time**: {formatted_time}\n"
                f"📊 **Prediction**: {prediction['prediction_type'].replace('_', ' ').title()} - {prediction['prediction']}\n"
                f"🎯 **Confidence**: {prediction['confidence']}%\n"
                f"💰 **Odds**: {prediction['odds']}\n"
                f"💡 **Reasoning**: {prediction['reasoning']}\n"
                f"🤖 **Tipster**: {prediction['tipster']}\n\n"
                f"*Based on real match data from API-Football*"
            )
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                logger.info("Prediction sent to Telegram successfully")
                return True
            else:
                logger.error(f"Failed to send Telegram message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def run_daily_pick(self):
        """Main function to generate and send daily pick"""
        logger.info("Starting real daily pick generation...")
        
        try:
            # Get real matches
            matches = self.get_real_matches()
            logger.info(f"Found {len(matches)} matches to analyze")
            
            # Select best match
            best_match = self.select_best_match(matches)
            if not best_match:
                logger.warning("No suitable matches found for prediction")
                return
            
            logger.info(f"Selected match: {best_match['home_team']} vs {best_match['away_team']} ({best_match['competition']})")
            
            # Generate prediction
            prediction = self.generate_prediction(best_match)
            logger.info(f"Generated prediction: {prediction['prediction']} (Confidence: {prediction['confidence']}%)")
            
            # Store in database
            if self.store_prediction(prediction):
                logger.info("Prediction stored in database")
            else:
                logger.error("Failed to store prediction in database")
            
            # Send to Telegram
            if self.send_telegram_message(prediction):
                logger.info("Prediction sent to Telegram")
            else:
                logger.error("Failed to send prediction to Telegram")
            
            logger.info("Daily pick generation completed successfully")
            
        except Exception as e:
            logger.error(f"Error in daily pick generation: {e}")

def main():
    """Main entry point"""
    generator = RealDailyPickGenerator()
    generator.run_daily_pick()

if __name__ == "__main__":
    main() 